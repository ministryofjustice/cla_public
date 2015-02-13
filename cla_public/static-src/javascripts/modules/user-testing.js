(function () {
  'use strict';

  moj.Modules.UserTesting = {
    el: '.form-actions',
    pt: '.phase-tag',
    scopeCheckerUrl: 'http://clap-user-testing.dsd.io/',
    covered: [
      {
        name: 'debt',
        checkerStartFilename: 'debt_and_housing.html'
      },
      {
        name: 'discrimination',
        checkerStartFilename: 'discrimination.html'
      },
      {
        name: 'education',
        checkerStartFilename: 'education.html'
      },
      {
        name: 'family',
        checkerStartFilename: 'family.html'
      },
      {
        name: 'housing',
        checkerStartFilename: 'debt_and_housing.html'
      },
      {
        name: 'violence',
        checkerStartFilename: 'domestic_violence.html'
      },
      {
        name: 'immigration',
        checkerStartFilename: 'immigration.html'
      }
    ],

    init: function() {
      if(this.userTestingAvailable()) {
        moj.log('testing available');
        this.cacheEls();
        this.bindEvents();
      }
    },

    cacheEls: function() {
      this.$phaseTag = $(this.pt);
      this.$submit = $(this.el).find('button[type="submit"]');
      this.$form = this.$submit.closest('form');
    },

    bindEvents: function() {
      var self = this;
      this.$phaseTag.on('dblclick', function(e) {
        e.preventDefault();
        self.enable();
      });

      $(document).on('click', '.fake-submit', function(e) {
        e.preventDefault();
        self.fakeSubmit();
      });

      $('input[name="categories"]').on('keypress keydown', function(e) {
        if(e.which === 13) {
          e.preventDefault();
          self.fakeSubmit();
        }
      });
    },

    userTestingAvailable: function() {
      var loc = document.location;
      var isProblemPage = (loc.pathname.indexOf('/problem') !== -1);
      var isDevOrDemo = (loc.hostname.indexOf('localhost') !== -1 || loc.hostname.indexOf('public-demo.cla.dsd.io') !== -1);
      return isDevOrDemo && isProblemPage;
    },

    enable: function() {
      this.$submit
        .hide()
        .before('<button class="button button-larger fake-submit">Continue</button>')
      ;
      this.$phaseTag.siblings('span').html('<strong>User Testing Enabled</strong>');

      moj.log('testing enabled');
    },

    getCategoryEl: function() {
      var $c = $('[name="categories"]:checked');
      return $c;
    },

    openScopeChecker: function(page) {
      var self = this;
      this.spawnedWindow = open(this.scopeCheckerUrl + page);
      this.spawnedWindow.focus();

      this.spawnedWindow.onunload = function() {
        self.realSubmit();
      };
    },

    fakeSubmit: function() {
      var self = this;
      var c = this.getCategoryEl();
      var startPage = '';

      for(var x = 0; x < this.covered.length; x = x + 1) {
        if(self.covered[x].name === c.val()) {
          startPage = self.covered[x].checkerStartFilename;
        }
      }

      if(startPage !== '') {
        moj.log('open prototype');
        self.openScopeChecker(startPage);
      } else {
        moj.log('stay in app');
        self.realSubmit();
      }
    },

    realSubmit: function() {
      $('.fake-submit').hide();
      this.$submit.show().trigger('click');
    }

  };
}());
