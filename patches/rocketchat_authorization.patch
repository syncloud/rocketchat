--- programs/server/packages/rocketchat_authorization.js   2018-01-23 19:05:47.184291810 +0000
+++ programs/server/packages/rocketchat_authorization.js.orig      2018-01-23 18:57:06.145994186 +0000
@@ -798,12 +798,12 @@
                        }).count();
                        const userIsAdmin = user.roles.indexOf('admin') > -1;

-                       //if (adminCount === 1 && userIsAdmin) {
-                       //      throw new Meteor.Error('error-action-not-allowed', 'Leaving the app without admins is not allowed', {
-                       //              method: 'removeUserFromRole',
-                       //              action: 'Remove_last_admin'
-                       //      });
-                       //}
+                       if (adminCount === 1 && userIsAdmin) {
+                               throw new Meteor.Error('error-action-not-allowed', 'Leaving the app without admins is not allowed', {
+                                       method: 'removeUserFromRole',
+                                       action: 'Remove_last_admin'
+                               });
+                       }
                }

                const remove = RocketChat.models.Roles.removeUserRoles(user._id, roleName, scope);
