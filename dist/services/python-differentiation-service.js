"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.pythonDifferentiationService = void 0;
const child_process_1 = require("child_process");
const readline_1 = require("readline");
class PythonDifferentiationService {
    process;
    readline;
    requestQueue = [];
    isProcessing = false;
    constructor() {
        this.startPythonProcess();
    }
    startPythonProcess() {
        this.process = (0, child_process_1.spawn)('python3', ['./scripts/differentiation.py']);
        this.readline = (0, readline_1.createInterface)({
            input: this.process.stdout,
            terminal: false
        });
        this.readline.on('line', (line) => {
            if (this.requestQueue.length > 0) {
                const { resolve, reject } = this.requestQueue.shift();
                try {
                    const response = JSON.parse(line);
                    if (response.error) {
                        reject(new Error(response.error));
                    }
                    else {
                        resolve(response.result);
                    }
                }
                catch (error) {
                    reject(new Error(`Failed to parse response: ${error.message}`));
                }
                this.processNextRequest();
            }
        });
        this.process.stderr?.on('data', (data) => {
            console.error(`Python service error: ${data.toString()}`);
            if (this.requestQueue.length > 0) {
                const { reject } = this.requestQueue.shift();
                reject(new Error(data.toString()));
                this.processNextRequest();
            }
        });
        this.process.on('close', () => {
            console.log('Python service closed, restarting...');
            setTimeout(() => this.startPythonProcess(), 1000);
        });
    }
    processNextRequest() {
        if (this.requestQueue.length > 0 && !this.isProcessing) {
            this.isProcessing = true;
            const { expression, variable } = this.requestQueue[0];
            this.process.stdin?.write(JSON.stringify({ expression, variable }) + '\n');
        }
        else {
            this.isProcessing = false;
        }
    }
    differentiate(expression, variable) {
        return new Promise((resolve, reject) => {
            this.requestQueue.push({ expression, variable, resolve, reject });
            this.processNextRequest();
        });
    }
}
exports.pythonDifferentiationService = new PythonDifferentiationService();
