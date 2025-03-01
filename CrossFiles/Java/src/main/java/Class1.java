import java.io.IOException;

public class Class1 {
    private String input;

    public Class1(String input) {
        this.input = input;
    }

    public void process() {
        System.out.println("Class1 processing: " + input);
        // Potentially unsafe operation
        try {
            Runtime.getRuntime().exec("echo " + input);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
