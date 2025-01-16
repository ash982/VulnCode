import { exec } from 'child_process';

export class Class1 {
    private input: string;

    constructor(input: string) {
        this.input = input;
    }

    public process(): void {
        console.log(`Class1 processing: ${this.input}`);
        // Potentially unsafe operation
        exec(`echo ${this.input}`, (error, stdout, stderr) => {
            if (error) {
                console.error(`exec error: ${error}`);
                return;
            }
            console.log(`stdout: ${stdout}`);
            console.error(`stderr: ${stderr}`);
        });
    }
}
