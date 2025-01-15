const { exec } = require('child_process');

class Class1 {
    constructor(input) {
        this.input = input;
    }

    process() {
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

module.exports = Class1;
