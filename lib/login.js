const inquirer = require('inquirer')

module.exports = {
    askLoginShopee: () => {
        const prom_login = [{
            name: "email/no",
            type: "input",
            message: "Masukan email/no akun shopee untuk login ke fs-bot.",
            validate: function( value ){
                if (value.length) {
                    return true
                } else {
                    return "Masukan Email/Nomer akun yang terdaftar di shopee yachh!"
                }
            }
        },{
            name: "Password",
            type: "password",
            message: "Masukan password akun anda",
            validate: function( value ){
                if (value.length) {
                    return true
                } else {
                    return "Masukin passnya ni biar bisa login"
                }
            }
        }]
        return inquirer.prompt(prom_login)
    }
}