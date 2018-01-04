conn = new Mongo();
db = conn.getDB("rocketchat");
cursor = db.rocketchat_settings.find();
while ( cursor.hasNext() ) {
   printjson( cursor.next() );
}
db.rocketchat_settings.update(
  { _id : "LDAP_Enable" },
  { $set : { value: true } }
);

cursor = db.rocketchat_settings.find();
while ( cursor.hasNext() ) {
   printjson( cursor.next() );
}