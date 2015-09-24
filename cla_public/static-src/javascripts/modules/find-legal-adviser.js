(function () {
  'use strict';

  moj.Modules.FindLegalAdviser = {
    el: '#resultsMap',
    markers: [],
    searchLocationMarker: null,
    openInfoWindow: null,
    eventsBound: false,

    init: function() {
      this.cacheEls();

      this._handleMQTest();

      if(!this.$resultsMap.length) {
        return;
      }

      this.renderMap(this.$resultsMap.data('lat'), this.$resultsMap.data('lon'));
      this._prepareMarkers();

      $(window).resize(_.debounce($.proxy(this._handleMQTest, this), 500));
    },

    // Handle events which rely on media queries
    _handleMQTest: function() {
      if(window.Modernizr.mq('(min-width: 641px)')) {
        if(!this.eventsBound) {
          this.bindEvents();
        }
      } else if(this.eventsBound) {
        this._unbindEvents();
      }
    },

    bindEvents: function() {
      var self = this;
      this.$organisationListItems.find('.org-summary').each(function() {
        $(this).replaceWith('<a class="' + this.className + '" aria-expanded="false" href="#">' + $(this).html() + '</a>');
      });

      this.$organisationListItems.on('click', '.org-summary', function(evt) {
        evt.preventDefault();
        self.$organisationListItems.find('.org-summary').attr('aria-expanded', false);
        $(this).attr('aria-expanded', true);
        self._handleItemHighlight(evt, $(this).closest('li'));
      });

      this.$resultsPagination.on('click', 'a', function(evt) {
        evt.preventDefault();

        if(window.LABELS && window.LABELS.loading) {
          $(evt.target).replaceWith('<span>' + window.LABELS.loading + '</span>');
        }

        self._fetchPage(evt.target.href);

        if(window.history && history.pushState) {
          history.pushState(null, null, evt.target.href);
        }
      });

      this.$findLegalAdviserForm.submit(function(evt) {
        evt.preventDefault();

        var url = document.location.pathname + '?' + $(this).serialize();
        self._fetchPage(url, true);

        if(window.history && history.pushState) {
          history.pushState(null, null, url);
        }

        if(!self.$resultsMap.length) {
          $('<p class="loading">' + window.LABELS.loading + '</p>').insertAfter($(this));
        }
      });

      window.onpopstate = function() {
        self._fetchPage(document.location.href);
      };

      this.eventsBound = true;
    },

    _unbindEvents: function() {
      this.$organisationListItems
        .unbind('click')
        .find('.org-summary')
        .each(function() {
          $(this).replaceWith('<header class="' + this.className + '">' + $(this).html() + '</header>');
        });

      this.$resultsPagination.unbind('click');
      this.$findLegalAdviserForm.unbind('submit');
      window.onpopstate = null;

      this.eventsBound = false;
    },

    _fetchPage: function(url, scrollToResults) {
      var self = this;

      $.get(url)
        .success(function(data) {
          self.$findLegalAdviserContainer.replaceWith(data);
          self.markers = [];
          self.eventsBound = false;
          self.init();

          if(scrollToResults) {
            $('html, body').delay(300).animate({
              'scrollTop': self.$findLegalAdviserContainer.offset().top - 10
            }, 160);
          }

          $('.search-results-list').attr('tabindex', -1).focus();

          ga('send', 'pageview', url);
        })
        .error();
    },

    _closeOpenInfoWindow: function() {
      if(this.openInfoWindow) {
        this.openInfoWindow.close();
      }
    },

    _prepareMarkers: function() {
      var organisations = $.map(this.$organisationListItems, function(item) {
        var $item = $(item);
        return {
          id: $item.data('id'),
          position: {
            lat: parseFloat($item.data('lat')),
            lng: parseFloat($item.data('lon'))
          },
          title: $item.find('.fn').text(),
          content: $item.html()
        };
      });

      this.addMarkers(organisations);
    },

    _fitAllMarkers: function() {
      var self = this;

      this.map.fitBounds(this.markers.reduce(function(bounds, marker) {
        return bounds.extend(marker.getPosition());
      }, new google.maps.LatLngBounds()));

      $.each(this.markers, function() {
        this.setMap(self.map);
      });
    },

    _handleHighlightedItemScroll: function($item, $container) {
      var itemHeight = $item.outerHeight();
      var containerHeight = $container.height();

      if(itemHeight + $item.position().top > containerHeight) {
        $container.scrollTop(containerHeight - itemHeight);
      }
    },

    _handleMarkersZooming: function(selectedMarkerId) {
      var markerOnMap = _.find(this.markers, { id: selectedMarkerId });

      $.each(this.markers, function() {
        this.setMap(null);
      });

      markerOnMap.setMap(this.map);

      var pairBounds = new google.maps.LatLngBounds();
      pairBounds.extend(markerOnMap.position);
      pairBounds.extend(this.searchLocationMarker.position);

      this.map.fitBounds(pairBounds);
    },

    _handleItemHighlight: function(evt, $item) {
      var $container = $item.closest('.search-results-list');

      if($item.hasClass('s-highlighted')) {
        this.$organisationListItems.removeClass('s-highlighted');
        this._fitAllMarkers();
        return;
      }

      this.$organisationListItems.removeClass('s-highlighted');
      $item.addClass('s-highlighted');

      $item.find('.org-details').attr('tabindex', -1).focus();

      this._handleMarkersZooming($item.data('id'));
      this._handleHighlightedItemScroll($item, $container);

      var count = $item.find('.marker').text();
      var name = $item.find('.fn').text();

      ga('send', 'event', 'find-legal-adviser', 'selected', count + ':' + name);
    },

    renderMap: function(lat, lon) {
      var self = this;

      var searchLocation = {
        lat: lat,
        lng: lon
      };

      var mapOptions = {
        center: searchLocation,
        zoom: 15,
        scrollwheel: false,
        panControl: false,
        streetViewControl: false
      };

      this.map = new google.maps.Map(this.$resultsMap[0], mapOptions);
      this.searchLocationMarker = this.addMarker(searchLocation, {
        title: 'Search location',
        icon: 'icon-location-2x'
      });

      google.maps.event.addListener(self.map, 'click', function() {
        self._closeOpenInfoWindow();
      });
    },

    addMarker: function(position, options) {
      var self = this;
      var image;
      options = options || {};

      if(options.icon) {
        image = {
          url: '/static/images/icons/' + options.icon + '.png',
          scaledSize: new google.maps.Size(16, 16),
          anchor: new google.maps.Point(8, 8)
        };
      } else if(options.id) {
        image = {
          url: '/static/images/icons/icon-numbered-markers-2x.png',
          size: new google.maps.Size(22, 40),
          scaledSize: new google.maps.Size(220, 40),
          origin: new google.maps.Point(22 * (options.id - 1), 0)
        };
      }

      var marker = new google.maps.Marker({
        position: position,
        id: options.id,
        title: options.title,
        map: this.map,
        icon: image
      });

      if(options.content) {
        google.maps.event.addListener(marker, 'click', function() {
          self._closeOpenInfoWindow();
          self.openInfoWindow = new google.maps.InfoWindow({
            content: options.content
          });
          self.openInfoWindow.open(self.map, marker);
        });
      }

      return marker;
    },

    addMarkers: function(points) {
      var self = this;

      $.each(points, function() {
        if(!(this.position)) {
          return;
        }
        self.markers.push(
          self.addMarker(this.position, {
            id: this.id,
            title: this.title,
            content: this.content
          })
        );
      });

      this._fitAllMarkers();
    },

    cacheEls: function() {
      this.$resultsMap = $(this.el);
      this.$findLegalAdviserContainer = $('.find-legal-adviser');
      this.$findLegalAdviserForm = $('.legal-adviser-search');
      this.$organisationListItems = $('.search-results-list .vcard');
      this.$resultsPagination = $('.search-results-pagination');
    }
  };
}());
