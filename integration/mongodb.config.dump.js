conn = new Mongo();
db = conn.getDB("rocketchat");

cursor = db.rocketchat_settings.find();
while ( cursor.hasNext() ) {
   printjson( cursor.next() );
}