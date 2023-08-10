import java.util.*; 
import java.net.URL;     
import org.apache.xmlrpc.*;
import org.apache.xmlrpc.client.XmlRpcClient;
import org.apache.xmlrpc.client.XmlRpcClientConfigImpl;
import java.util.Scanner;

public class Client {
    public static void main (String [] args) {
        if(args.length == 0) {
            System.out.println("Usage: java Client <server>");
            System.exit(1);
        }
        // initialize the server connection
        XmlRpcClientConfigImpl config = new XmlRpcClientConfigImpl();
        XmlRpcClient client = null;
        try {
            config.setServerURL(new URL("http://" + args[0] + ":" + 8854));
            client = new XmlRpcClient();
            client.setConfig(config);
        } catch (Exception e) {
            System.err.println("Client error: "+ e);
            System.exit(1);
        }

        System.out.println("Welcome to the bookstore");
        System.out.println("Enter \"help\" for usage hints");

        Scanner scan = new Scanner(System.in);
        System.out.print("> ");
        while (scan.hasNext()){
            stringParser(scan.nextLine(),client);
            System.out.print("> ");
        }
    }

    /*
     * stringParser(input, client) - Parses the requested queries
     */
    private static void stringParser(String input, XmlRpcClient client) {
        String[] tokens = input.split(" ", 2); 

        String invalidReq = "Invalid Request ... Enter \"help\" for usage hints";

        switch(tokens[0]) {
            case "lookup":
                if (isNumeric(tokens[1])){
                    System.out.println(lookup(Integer.parseInt(tokens[1]), client));
                } else {
                    System.out.println(invalidReq);
                }
                break;
            case "search":
                System.out.println(search(tokens[1], client));
                break;
            case "buy":
                if (isNumeric(tokens[1])) {
                    System.out.println(buy(Integer.parseInt(tokens[1]), client));
                } else {
                    System.out.println(invalidReq);
                }
                break;
            case "help":
                System.out.println("lookup <item_number> | look up a book using their item number");
                System.out.println("search <topic> | search for a book under a specific topic");
                System.out.println("buy <item_number> | buy the book using their item hunber");
                System.out.println("leave | Want to leave the bookstore?");
                break;
            case "leave":
                System.out.println("You left the bookstore");
                System.exit(0);
                break;
            default:
                System.out.println(invalidReq);
        }
    }

    /*
     * helper function that checks to see if a string is
     * an numeric
     */
    private static boolean isNumeric(String string) {
        int intValue;
            
        if(string == null || string.equals("")) {
            return false;
        }
        
        try {
            intValue = Integer.parseInt(string);
            return true;
        } catch (NumberFormatException e) {
            return false;
        }
    }

    /*
     * search(topic, client) - allows the user to specify a 
     * topic (or category) and returns all entries belonging 
     * to that category (a title and an item number are 
     * displayed for each match).
     */
    public static String search (String topic, XmlRpcClient client) {
        Vector<Object> params = new Vector<Object>();
        params.addElement(topic);
        String output = "";
        try{
            Object[] result = (Object[]) client.execute("sample.search", params.toArray());
            for (int i = 0; i < result.length; i++) {
                if (i + 1 == result.length) {
                    output += ((String)result[i]);
                } else {
                    output += ((String)result[i] + "\n");
                } 
            }
        } catch (Exception e) {
            System.err.println("Client search error: " + e);
        }
        return output;
    }

    /*
     * lookup(item_number, client) - allows an item number to be 
     * specified and returns details such as title, cost, subject, 
     * and whether or not the item is in stock.
     */
    public static String lookup (Integer item_number, XmlRpcClient client) {
        Vector<Object> params = new Vector<Object>();
        params.addElement(item_number);
        String output = "";
        try{
            Object[] result = (Object[]) client.execute("sample.lookup", params.toArray());
            for (int i = 0; i < result.length; i++) {
                output += ((String)result[i]); 
            }
        } catch (Exception e) {
            System.err.println("Client lookup error: " + e);
        }
        return output;
    }

    /*
     * buy(item_number, client) - specifies an item number for 
     * purchase (assume the desired quantity is always 1).
    */
    public static String buy (Integer item_number, XmlRpcClient client) {
        Vector<Object> params = new Vector<Object>();
        params.addElement(item_number);
        String output = "";
        try{
            Object[] result = (Object[]) client.execute("sample.buy", params.toArray());
            if (result.length == 0) {
                return "Error buying book. Please try again";
            }
            for (int i = 0; i < result.length; i++) {
                output += ((String)result[i]);
            }
        } catch (Exception e) {
            System.err.println("Client buy error: " + e);
        }
        return output;
    }

}
