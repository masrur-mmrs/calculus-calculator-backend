import { spawn, ChildProcess } from 'child_process';
import { createInterface, Interface } from 'readline';

interface QueueItem {
  expression: string;
  variable: string;
  bound: object;
  resolve: (value: string) => void;
  reject: (reason: Error) => void;
}

interface PythonResponse {
  result?: string;
  error?: string;
}

interface Bound {
  upperBound: string;
  lowerBound: string;
}

class PythonIntegrationService {
  private process!: ChildProcess;
  private readline!: Interface;
  private requestQueue: QueueItem[] = [];
  private isProcessing: boolean = false;

  constructor() {
    this.startPythonProcess();
  }

  private startPythonProcess(): void {
    this.process = spawn('python3', ['./scripts/integration.py']);
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
      console.error(`Python integration service error: ${data.toString()}`);
      if (this.requestQueue.length > 0) {
        const { reject } = this.requestQueue.shift()!;
        reject(new Error(data.toString()));
        this.processNextRequest();
      }
    });

    this.process.on('close', () => {
      console.log('Python integration service closed, restarting...');
      setTimeout(() => this.startPythonProcess(), 1000);
    });
  }

  private processNextRequest(): void {
    if (this.requestQueue.length > 0 && !this.isProcessing) {
      this.isProcessing = true;
      const { expression, variable, bound } = this.requestQueue[0];
      this.process.stdin?.write(JSON.stringify({ expression, variable, bound }) + '\n');
    } else {
      this.isProcessing = false;
    }
  }

  public integrate(expression: string, variable: string, bound: Bound): Promise<string> {
    return new Promise<string>((resolve, reject) => {
      this.requestQueue.push({ expression, variable, bound, resolve, reject });
      this.processNextRequest();
    });
  }
}

export const pythonIntegrationService = new PythonIntegrationService();