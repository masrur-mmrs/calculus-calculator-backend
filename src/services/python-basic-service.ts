import { spawn, ChildProcess } from 'child_process';
import { createInterface, Interface } from 'readline';

interface QueueItem {
  expression: string;
  resolve: (value: { exact: string; decimal: number }) => void;
  reject: (reason: Error) => void;
}

interface PythonResponse {
  result?: {
    exact: string;
    decimal: number;
  };
  error?: string;
}

class PythonBasicService {
  private process!: ChildProcess;
  private readline!: Interface;
  private requestQueue: QueueItem[] = [];
  private isProcessing: boolean = false;

  constructor() {
    this.startPythonProcess();
  }

  private startPythonProcess(): void {
    this.process = spawn('python3', ['./scripts/basic.py']);
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
            resolve(response.result!);
          }
        } catch (error) {
          reject(new Error(`Failed to parse response: ${(error as Error).message}`));
        }
        this.processNextRequest();
      }
    });

    this.process.stderr?.on('data', (data: Buffer) => {
      console.error(`Python basic service error: ${data.toString()}`);
      if (this.requestQueue.length > 0) {
        const { reject } = this.requestQueue.shift()!;
        reject(new Error(data.toString()));
        this.processNextRequest();
      }
    });

    this.process.on('close', () => {
      console.log('Python basic service closed, restarting...');
      setTimeout(() => this.startPythonProcess(), 1000);
    });
  }

  private processNextRequest(): void {
    if (this.requestQueue.length > 0 && !this.isProcessing) {
      this.isProcessing = true;
      const { expression } = this.requestQueue[0];
      // Note: We need to write a complete JSON object that includes the newline
      this.process.stdin?.write(JSON.stringify({ expression }) + '\n');
    } else {
      this.isProcessing = false;
    }
  }

  public evaluateExpression(expression: string): Promise<{ exact: string; decimal: number }> {
    return new Promise<{ exact: string; decimal: number }>((resolve, reject) => {
      this.requestQueue.push({ expression, resolve, reject });
      this.processNextRequest();
    });
  }
}

export const pythonBasicService = new PythonBasicService();