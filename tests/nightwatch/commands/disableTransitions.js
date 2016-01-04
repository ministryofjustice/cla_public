'use strict';

// Disable transitions

exports.command = function() {
  var client = this;

  this.perform(function() {
    client.execute(function() {
      $('html head').append('<style>*, *:before, *:after { transition: none !important; -webkit-transition: none !important }</style>');
    });

    return client;
  });
};
