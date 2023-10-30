import protobuf from "protobufjs";

export default async function getData() {
  try {
    // make a network request to fetch the protobuf data
    const response = await fetch(
      "https://ai-landscape-visualizer.s3.us-west-1.amazonaws.com/client_side.protobuf",
    );

    // read the response as an ArrayBuffer
    const text = await response.arrayBuffer();
    // convert the ArrayBuffer to a Uint8Array
    const uint8Array = new Uint8Array(text);
    // load the protobuf schema
    const root = await protobuf.load("/client_side.proto");
    // retrieve the data type definition from the protobuf schema
    const data = root.lookupType("Data");
    // decode the binary message using the data type definition
    const message = data.decode(uint8Array);
    // convert the protobuf message to a JavaScript object
    const object = data.toObject(message, {
      longs: Number,
      enums: String,
      bytes: String,
      arrays: true,
    });

    // extract the data array from the object
    const dataArray = object.conferences.map((conference) =>
      conference.years.map((year) => year.papers),
    );

    // return the extracted data
    return dataArray;
  } catch (error) {
    // handle any errors that occur during the process and log them
    console.error(error);
  }
}
