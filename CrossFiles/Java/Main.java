public class Main {
    public static void main(String[] args) {
        if (args.length < 1) {
            System.out.println("Usage: java Main <input>");
            return;
        }

        String taintedInput = args[0];

        Class1 obj1 = new Class1(taintedInput);
        Class2 obj2 = new Class2(taintedInput);

        obj1.process();
        obj2.process();
    }
}
