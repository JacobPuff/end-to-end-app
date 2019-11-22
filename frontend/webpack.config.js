const path = require('path');

module.exports = {
    mode: 'development',
    entry: {
        "login-signup": './src/login-signup.js',
        verify: './src/verify.js',
        forgotpassword: './src/forgotpassword.js',
        passwordreset: './src/passwordreset.js',
        yourprofile: './src/yourprofile.js',
        homePage: './src/homePage.js',
        tasklists: './src/tasklists/listOfLists.js'
    },
    devtool: 'eval',
    output: {
        filename: '[name].js',
        path: path.resolve(__dirname, 'dist'),
    },
};