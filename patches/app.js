--- programs/server/app/app.js  2018-01-23 18:48:13.937898268 +0000
+++ programs/server/app/app.js.orig     2018-01-23 18:44:18.163204638 +0000
@@ -7410,12 +7410,12 @@
                }).count();
                const userIsAdmin = user.roles.indexOf('admin') > -1;

-               //if (adminCount === 1 && userIsAdmin) {
-               //      throw new Meteor.Error('error-action-not-allowed', 'Leaving the app without admins is not allowed', {
-               //              method: 'deleteUser',
-               //              action: 'Remove_last_admin'
-               //      });
-               //}
+               if (adminCount === 1 && userIsAdmin) {
+                       throw new Meteor.Error('error-action-not-allowed', 'Leaving the app without admins is not allowed', {
+                               method: 'deleteUser',
+                               action: 'Remove_last_admin'
+                       });
+               }

                RocketChat.deleteUser(userId);
                return true;
