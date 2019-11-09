const path = require('path');

module.exports = {
    mode: 'development',
    entry: {
        //main: './src/index.html',
        tasklists: './src/tasklists/tasklists.js'
    },
    devtool: 'eval',
    output: {
        filename: 'main.js',
        path: path.resolve(__dirname, 'dist/tasklists'),
    },
};