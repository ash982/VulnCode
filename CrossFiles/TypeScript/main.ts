import { Class1 } from './Class1';
import { Class2 } from './Class2';

function main() {
    const args = process.argv.slice(2);
    if (args.length < 1) {
        console.log("Usage: ts-node main.ts <input>");
        return;
    }

    const taintedInput: string = args[0];

    const obj1 = new Class1(taintedInput);
    const obj2 = new Class2(taintedInput);

    obj1.process();
    obj2.process();
}

main();

