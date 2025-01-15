const Class1 = require('./class1');
const Class2 = require('./class2');

function main() {
    if (process.argv.length < 3) {
        console.log(`Usage: node ${process.argv[1]} <input>`);
        return;
    }

    const taintedInput = process.argv[2];

    const obj1 = new Class1(taintedInput);
    const obj2 = new Class2(taintedInput);

    obj1.process();
    obj2.process();
}

main();
