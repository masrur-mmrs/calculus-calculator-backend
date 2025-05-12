import { spawn, ChildProcess } from 'child_process';
import { createInterface, Interface } from 'readline';

interface QueueItem {
    expression: string;
    variable: string;
    orderOfDerivative: string;
    resolve: (value: string) => void;
    reject: (reason: Error) => void;
}

interface PythonResponse {
    simplified?: string;
    steps: Object[];
    result?: string;
    error?: string;
}

class PythonDerivativeStepsService {
    private process!: ChildProcess;
    private readline!: Interface;
    private requestQueue: QueueItem[] = [];
    private isProcessing: boolean = false;

    constructor() {
        this.startPythonProcess();
    }

    private startPythonProcess(): void {
        this.process = spawn('python3', ['./scripts/differentiation_steps.py']);
        this.readline = createInterface({
            input: this.process.stdout as NodeJS.ReadableStream,
            terminal: false
        });

        this.readline.on('line', (line: string) => {
            if (this.requestQueue.length > 0) {
                const { resolve, reject } = this.requestQueue.shift()!;
                
                try {
                    const response: PythonResponse = JSON.parse(line);
                    if (response.error) {
                        reject(new Error(response.error));
                    } else {
                        resolve(JSON.stringify({
                            simplified: response.simplified,
                            steps: response.steps,
                            result: response.result
                        }));
                    }
                } catch (error) {
                    reject(new Error(`Failed to parse response: ${(error as Error).message}`));
                }
                
                this.processNextRequest();
            }
        });

        this.process.stderr?.on('data', (data: Buffer) => {
            console.error(`Python service error: ${data.toString()}`);
            if (this.requestQueue.length > 0) {
                const { reject } = this.requestQueue.shift()!;
                reject(new Error(data.toString()));
                this.processNextRequest();
            }
        });

        this.process.on('close', () => {
            console.log('Python service closed, restarting...');
            setTimeout(() => this.startPythonProcess(), 1000);
        });
    }

    private processNextRequest(): void {
        if (this.requestQueue.length > 0 && !this.isProcessing) {
            this.isProcessing = true;
            const { expression, variable, orderOfDerivative } = this.requestQueue[0];
            this.process.stdin?.write(JSON.stringify({ expression, variable, orderOfDerivative }) + '\n');
        } else {
            this.isProcessing = false;
        }
    }

    public differentiate_with_steps(expression: string, variable: string, orderOfDerivative: string): Promise<string> {
        return new Promise((resolve, reject) => {
            this.requestQueue.push({ expression, variable, orderOfDerivative, resolve, reject });
            if (!this.isProcessing) {
                this.processNextRequest();
            }
        });
    }
}

export const pythonDerivativeStepsService = new PythonDerivativeStepsService();