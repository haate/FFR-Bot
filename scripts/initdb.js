    use admin
    db.createUser({user: "admin", pwd: "password", roles: [{role: "userAdminAnyDatabase", db: "admin"}, "readWriteAnyDatabase" ]})
    db.adminCommand({shutdown: 0})