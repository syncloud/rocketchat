conn = new Mongo();
db = conn.getDB("rocketchat");

//"valueSource" : "meteorSettingsValue",

db.rocketchat_settings.update(
  { _id : "LDAP_Enable" },
  { $set : { meteorSettingsValue: true } }
);

db.rocketchat_settings.update(
  { _id : "LDAP_Host" },
  { $set : { meteorSettingsValue: "localhost" } }
);

db.rocketchat_settings.update(
  { _id : "LDAP_BaseDN" },
  { $set : { meteorSettingsValue: "dc=syncloud,dc=org" } }
);

db.rocketchat_settings.update(
  { _id : "LDAP_Authentication" },
  { $set : { meteorSettingsValue: true } }
);

db.rocketchat_settings.update(
  { _id : "LDAP_Authentication_UserDN" },
  { $set : { meteorSettingsValue: "dc=syncloud,dc=org" } }
);

db.rocketchat_settings.update(
  { _id : "LDAP_Authentication_Password" },
  { $set : { meteorSettingsValue: "syncloud" } }
);

db.rocketchat_settings.update(
  { _id : "LDAP_User_Search_Filter" },
  { $set : { meteorSettingsValue: "(objectclass=inetOrgPerson)" } }
);

db.rocketchat_settings.update(
  { _id : "LDAP_User_Search_Field" },
  { $set : { meteorSettingsValue: "cn" } }
);

db.rocketchat_settings.update(
  { _id : "LDAP_Username_Field" },
  { $set : { meteorSettingsValue: "cn" } }
);

db.rocketchat_settings.update(
  { _id : "Accounts_RegistrationForm" },
  { $set : { meteorSettingsValue: "Public" } }
);
db.rocketchat_settings.update(
  { _id : "LDAP_Internal_Log_Level" },
  { $set : { meteorSettingsValue: "debug" } }
);

/*
cursor = db.rocketchat_settings.find();
while ( cursor.hasNext() ) {
   printjson( cursor.next() );
}
*/
