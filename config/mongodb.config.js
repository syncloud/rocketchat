conn = new Mongo();
db = conn.getDB("rocketchat");

printjson(db.rocketchat_settings.update(
  { _id : "LDAP_Enable" },
  { $set : { value: true } }
));

db.rocketchat_settings.update(
  { _id : "LDAP_Host" },
  { $set : { value: "localhost" } }
);

db.rocketchat_settings.update(
  { _id : "LDAP_Reject_Unauthorized" },
  { $set : { value: false } }
);

db.rocketchat_settings.update(
  { _id : "LDAP_BaseDN" },
  { $set : { value: "dc=syncloud,dc=org" } }
);

db.rocketchat_settings.update(
  { _id : "LDAP_Authentication" },
  { $set : { value: true } }
);

db.rocketchat_settings.update(
  { _id : "LDAP_Authentication_UserDN" },
  { $set : { value: "dc=syncloud,dc=org" } }
);

db.rocketchat_settings.update(
  { _id : "LDAP_Authentication_Password" },
  { $set : { value: "syncloud" } }
);

db.rocketchat_settings.update(
  { _id : "LDAP_User_Search_Filter" },
  { $set : { value: "(objectclass=inetOrgPerson)" } }
);

db.rocketchat_settings.update(
  { _id : "LDAP_User_Search_Field" },
  { $set : { value: "cn" } }
);

db.rocketchat_settings.update(
  { _id : "LDAP_Username_Field" },
  { $set : { value: "cn" } }
);

db.rocketchat_settings.update(
  { _id : "Accounts_RegistrationForm" },
  { $set : { value: "Public" } }
);
db.rocketchat_settings.update(
  { _id : "LDAP_Internal_Log_Level" },
  { $set : { value: "debug" } }
);

/*
cursor = db.rocketchat_settings.find();
while ( cursor.hasNext() ) {
   printjson( cursor.next() );
}
*/
