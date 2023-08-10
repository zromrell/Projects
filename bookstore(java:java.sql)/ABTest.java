import org.apache.xmlrpc.webserver.WebServer;
import org.apache.xmlrpc.server.XmlRpcServer;
import org.apache.xmlrpc.server.PropertyHandlerMapping;
import org.apache.xmlrpc.XmlRpcException;
import java.sql.*;
import java.util.*;
import java.net.URL;
import org.apache.xmlrpc.*;
import java.util.Scanner;
import java.io.*;
import java.net.URL;
import org.apache.xmlrpc.client.XmlRpcClient;
import org.apache.xmlrpc.client.XmlRpcClientConfigImpl;
import java.util.concurrent.locks.ReentrantLock;
import java.util.concurrent.TimeUnit;
import java.util.Date;

public class BookstoreTest extends Thread {
    private static Vector<Long> times = new Vector<Long>();
    private final ReentrantLock lock = new ReentrantLock();

    public static void main (String [] args) {
        if(args.length == 0) {
            System.out.println("Usage: java Client <server>");
            System.exit(1);
        }
        // initialize the server connection
        XmlRpcClientConfigImpl config = new XmlRpcClientConfigImpl();
        XmlRpcClient client=null;
        try {
            config.setServerURL(new URL("http://" + args[0] + ":" + 8854));
            client = new XmlRpcClient();
            client.setConfig(config);
        } catch (Exception e) {
            System.err.println("Client error: "+ e);
        }

        // TEST 1: make 500 successive buy calls
        /*
        for(int i = 0; i < 500; i++) {
            System.out.println(search("distributed systems", client));
        }
        System.out.println("First test complete");
        */
        //TEST 2: make concurrent buy calls from multiple threads

        Vector<Thread> test2 = new Vector<Thread>();
        for(int i = 0; i < 1; i++) {
            Thread thread = new BookstoreTest();
            System.out.println("Thread is being created");
            test2.add(thread);
            thread.start();
        }

        try {
            for(int i = 0; i < 10; i++) {
                test2.get(i).join();
            }
        } catch(Exception e) {

        }
        System.out.println(times);
    }

    public void run(){
        //Start time
        long begin = System.currentTimeMillis();
        // initialize the server connection
        XmlRpcClientConfigImpl config = new XmlRpcClientConfigImpl();
        XmlRpcClient client=null;
        try {
            config.setServerURL(new URL("http://localhost:" + 8854));
            client = new XmlRpcClient();
            client.setConfig(config);
        } catch (Exception e) {
            System.err.println("Client error: "+ e);
        }

        System.out.println("Thread is running");
        //long begin = System.currentTimeMillis();
        for(int i = 0; i < 500; i++) {
            search("distributed systems", client);
        }
        //End time
        long end = System.currentTimeMillis();
        long time = end-begin;
        lock.lock();
        times.add(time);
        lock.unlock();
        
    }

    
    public static String search (String topic, XmlRpcClient client) {
        // calling some function
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
                //System.out.println((String)result[i]);
            }
        } catch (Exception e) {
            System.err.println("Client error: " + e);
        }
        return output;
    }

    //can combine lookup and buy in a single method with another parameter
    public static String lookup (Integer item_number, XmlRpcClient client) {
        // calling some function
        Vector<Object> params = new Vector<Object>();
        params.addElement(item_number);
        //params.addElement("distributed systems");
        String output = "";
        try{
            Object[] result = (Object[]) client.execute("sample.lookup", params.toArray());
            for (int i = 0; i < result.length; i++) {
                output += ((String)result[i]);
                //System.out.println((String)result[i]);
            }
        } catch (Exception e) {
            System.err.println("Client error: " + e);
        }
        return output;
    }

    public static String buy (Integer item_number, XmlRpcClient client) {
        // calling some function
        Vector<Object> params = new Vector<Object>();
        params.addElement(item_number);
        //params.addElement("distributed systems");
        String output = "";
        try{
            Object[] result = (Object[]) client.execute("sample.buy", params.toArray());
            if (result.length == 0) {
                return "Error buying book. Please try again";
            }
            for (int i = 0; i < result.length; i++) {
                output += ((String)result[i]);
                //System.out.println((String)result[i]);
            }
        } catch (Exception e) {
            System.err.println("Client buy error: " + e);
        }
        return output;
    }

}

