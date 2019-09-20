var UnminifiedWebpackPlugin = require('unminified-webpack-plugin');
var UglifyJsPlugin = require('uglifyjs-webpack-plugin');
const path = require('path');
var common = {
      mode: 'production',
      output: {filename: 'cla.min.js'},
      target: 'web',
      optimization: {
        minimizer: [new UglifyJsPlugin({
            uglifyOptions: {
                compress: false,
                output: {
                    comments: false,
                },
            }
        })],
      },
      plugins: [
          new UnminifiedWebpackPlugin()
      ],
      resolve: {
        alias: {
          govuk_publishing_components: path.resolve(__dirname,"../node_modules/govuk_publishing_components/app/assets/javascripts/govuk_publishing_components")
        }
      }
}

module.exports = common;
