import java.sql._
import org.apache.spark.sql.SparkSession
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import org.apache.spark.sql.streaming.Trigger

// define postgresql sink
class PostgreSqlSink() extends org.apache.spark.sql.ForeachWriter[org.apache.spark.sql.Row] {
    val driver = "org.postgresql.Driver"
    var connection: java.sql.Connection = _
    var statement: java.sql.PreparedStatement = _

    val config = ConfigFactory.load("application.conf").getConfig("com.ram.batch") 
    val sparkConfig = config.getConfig("spark")
    val postgresConfig = config.getConfig("postgres")

    def open(partitionId: Long, version: Long): Boolean = {
        Class.forName(driver)
        connection = java.sql.DriverManager.getConnection(url, user, pwd)
        connection.setAutoCommit(false)
        statement = connection.prepareStatement(v_sql)
        true
    }

  // process each tweet (row)
    // copied directly from: https://sonra.io/spark/advanced-spark-structured-streaming-aggregations-joins-checkpointing/ 
    def process(value: org.apache.spark.sql.Row): Unit = {
        statement.executeUpdate(
            "DELETE FROM stream_tweets WHERE stream_tweets.language_code = '" + value(0) + "' ; "
        )
        statement.executeUpdate(
            "INSERT INTO stream_tweets VALUES('" +value(0)+ "', " +value(1)+ ", " +value(2)+ ", '" +value(3)+ "');"
        )
        }
    def close(errorOrNull: Throwable): Unit = {
        connection.commit()
        connection.close
  }
}

// configure Spark Session
val spark = SparkSession
    .builder()
    .appName("Twitter Streaming")
    .master("local[*]")
    .getOrCreate()

// define database urls
val jdbcWriter = new PostgreSqlSink()


// Define data source
// here, it's the Kafka broker: tweetStream.get_twitter_data()
val data_stream = spark
    .readStream // constantly expanding dataframe
    .format("kafka")
    .option("kafka.bootstrap.servers", "localhost:9092")
    .option("subscribe", "data-tweets")
    .option("startingOffsets","latest") //or earliest
    .load()

// watermarking to mark late-arriving data
var data_stream_transformed = data_stream
    .withWatermark("timestamp","1 day")

 // incoming tweet schema
val schema = StructType(Seq(
        StructField("created_at", StringType, true),
        StructField("id", StringType, true),
        StructField("id_str", StringType, true),
        StructField("text", StringType, true),
        StructField("retweet_count", StringType, true),
        StructField("favorite_count", StringType, true),
        StructField("favorited", StringType, true),
        StructField("retweeted", StringType, true),
        StructField("lang", StringType, true),
        StructField("location", StringType, true)
    ))

// data transformations
data_stream_transformed = data_stream_transformed
      .selectExpr("CAST(value AS STRING) as json") // byte --> string
      .select(from_json(col("json"),schema=schema).as("tweet")) // json string --> table defined by schema
      .selectExpr( // data type casts
       "tweet.created_at",
       "cast (tweet.id as long)",
       "tweet.id_str",
       "tweet.text",
       "cast (tweet.retweet_count as integer)",
       "cast (tweet.favorite_count as integer)" ,
       "cast(tweet.favorited as boolean)" ,
       "cast(tweet.retweeted as boolean)",
       "tweet.lang as language_code"
    ) // result = json tweets formatted in df

// group tweets by language code & count number of likes per tweet author
data_stream_transformed = data_stream_transformed
  .groupBy("language_code")
  .agg(sum("favorite_count"), count("id"))

