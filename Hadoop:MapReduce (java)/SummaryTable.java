/**
 * MapReduce job that pipes input to output as MapReduce-created key-val pairs
 */

import java.io.IOException;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.conf.Configuration;
import org.apache.hadoop.mapreduce.Job;
import org.apache.hadoop.mapreduce.Mapper;
import org.apache.hadoop.mapreduce.Reducer;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.json.simple.*;

// /usr/cs-local/339/hadoop/bin/hadoop jar build.jar SummaryTable ./clicks_merged/clicks.log ./impressions_merged/impressions.log output
//  hadoop jar build.jar SummaryTable /user/input/clicks.log /user/input/impressions.log /user/output 
// hdfs dfs -cat /user/output/part-r-00000

/**
 * Trivial MapReduce job that pipes input to output as MapReduce-created key-value pairs.
 */
public class SummaryTable {

public static void main(String[] args) throws Exception {
	if (args.length < 2) {
		System.err.println("Error: Wrong number of parameters");
		System.err.println("Expected: [in] [out]");
		System.exit(1);
	}

	Configuration conf = new Configuration();
	
	//Job1
	Job job = Job.getInstance(conf, "SummaryTable job");
	job.setJarByClass(SummaryTable.class);

	// set the Mapper and Reducer functions we want
	job.setMapperClass(SummaryTable.MapperOne.class);
	job.setReducerClass(SummaryTable.ReducerOne.class);
	job.setMapOutputKeyClass(Text.class);
	job.setOutputKeyClass(Text.class);

	// input arguments tell us where to get/put things in HDFS
	FileInputFormat.addInputPath(job, new Path(args[0]));
	FileInputFormat.addInputPath(job, new Path(args[1]));

	//FileOutputFormat.setOutputPath(job, new Path(args[2]));
	//FileOutputFormat.setOutputPath(job, new Path("/user/temp"));
	FileOutputFormat.setOutputPath(job, new Path("./temp"));
	//FileOutputFormat.setOutputPath(job, new Path(args[1]));
	//System.exit(job.waitForCompletion(true) ? 0 : 1);
	job.waitForCompletion(true);

	//Job2

	Job job2 = Job.getInstance(conf, "SummaryTable job2");
	job2.setJarByClass(SummaryTable.class);

	// set the Mapper and Reducer functions we want
	job2.setMapperClass(SummaryTable.MapperTwo.class);
	job2.setReducerClass(SummaryTable.ReducerTwo.class);
	job2.setMapOutputKeyClass(Text.class);

	// input arguments tell us where to get/put things in HDFS
	//FileInputFormat.addInputPath(job2,  new Path("/user/temp"));
	FileInputFormat.addInputPath(job2,  new Path("./temp"));
	FileOutputFormat.setOutputPath(job2, new Path(args[2]));

	// ternary operator - a compact conditional that just returns 0 or 1
	System.exit(job2.waitForCompletion(true) ? 0 : 1);
}

/**
 * map: (LongWritable, Text) --> (LongWritable, Text)
 * NOTE: Keys must implement WritableComparable, values must implement Writable
 */
public static class MapperOne extends Mapper < LongWritable, Text, 
                                                    Text, Text > {

	@Override
	public void map(LongWritable key, Text val, Context context)
		throws IOException, InterruptedException {
		// write (key, val) out to memory/disk
		// uncomment for debugging
        JSONObject object = (JSONObject) JSONValue.parse(val.toString());
		String key1 = "";
		String val1 = "";
		key1 = object.get("impressionId").toString();

		if (object.containsKey("referrer")) {
			val1 = String.format("%s, %s", object.get("referrer"), object.get("adId"));
		} else {
			val1 = "1";
		}
		
		//System.out.println("key: "+key1+" val: "+val1);
		context.write(new Text(key1), new Text(val1));
		/*
        /usr/cs-local/339/hadoop/bin/hadoop jar build.jar SummaryTable hello.txt output
        cat output/part-r-00000
        rm -rf output/
		hdfs dfs -cat /user/output/part-r-00000
        */
		
	}

}

/**
 * reduce: (LongWritable, Text) --> (LongWritable, Text)
 */
public static class ReducerOne extends Reducer < Text, Text, 
                                                      Text, Text > {

	@Override
	public void reduce(Text key, Iterable < Text > values, Context context) 
		throws IOException, InterruptedException {
		// write (key, val) for every value

		String key1 = "";
		String val1 = "0";

		for (Text val : values) {
			if (val.toString().contains(",")) {
				key1 = String.format("[%s]", val.toString());
			} else {
				val1 = "1";
			}
		}
		context.write(new Text(key1), new Text(val1));
	}
}

public static class MapperTwo extends Mapper < LongWritable, Text, 
                                                    Text, Text > {

	@Override
	public void map(LongWritable key, Text val, Context context)
		throws IOException, InterruptedException {
		// write (key, val) out to memory/disk
		// uncomment for debugging
        
		int splitter = val.toString().indexOf("]");

		String key1 = (val.toString().substring(0, splitter+1));
		String val1 = (val.toString().substring(splitter+1));

		if (val1.contains("0")) {
			val1 = "0";
		} else {
			val1 = "1";
		}
		
		//System.out.println("key: "+key1+"          val: "+val1);
		context.write(new Text(key1), new Text(val1));
	}

}

/**
 * reduce: (LongWritable, Text) --> (LongWritable, Text)
 */
public static class ReducerTwo extends Reducer < Text, Text, 
                                                      Text, Text > {

	@Override
	public void reduce(Text key, Iterable < Text > values, Context context) 
		throws IOException, InterruptedException {
		// write (key, val) for every value
		double total = 0;
		double count = 0;
		double clickThru = 0.0;

		for (Text val : values) {
			count += (double) Integer.parseInt(val.toString());
			total += 1.0; 
		}

		clickThru = count/total;

		context.write(key, new Text(String.valueOf(clickThru)));
	}

}
    
}
