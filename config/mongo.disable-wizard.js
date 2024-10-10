use rocketchat
db.rocketchat_settings.update({"_id": "Show_Setup_Wizard"}, {$set: {'value': 'completed'}})
