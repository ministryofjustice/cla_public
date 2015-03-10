(function () {
  'use strict';

  moj.Modules.FindLegalAdviser = {
    el: '#resultsMap',
    markers: [],
    searchLocationMarker: null,
    openInfoWindow: null,

    init: function() {
      this.cacheEls();

      if(!this.resultsMap.length) {
        return;
      }

      this.bindEvents();

      this.renderMap(this.resultsMap.data('lat'), this.resultsMap.data('lon'));

      var organisations = $.map(this.organisationListItems, function(item) {
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

      $(window).load($.proxy(function() {
        this._scrollToResults();
      }, this));
    },

    bindEvents: function() {
      var self = this;
      this.organisationListItems.on('click', function(evt) {
        self._handleItemHighlight(evt, this);
      });
    },

    _scrollToResults: function() {
      $('html, body').animate({
        scrollTop: this.findLegalAdviserContainer.offset().top - 10
      }, 120);
    },

    _closeOpenInfoWindow: function() {
      if(this.openInfoWindow) {
        this.openInfoWindow.close();
      }
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

    _handleItemHighlight: function(evt, item) {
      var $item = $(item);
      var $container = $item.closest('.search-results-list');

      // Exclude links
      if($(evt.target).is('a')) {
        return;
      }

      if($item.hasClass('s-highlighted')) {
        this.organisationListItems.removeClass('s-highlighted');
        this._fitAllMarkers();
        return;
      }

      this.organisationListItems.removeClass('s-highlighted');
      $item.addClass('s-highlighted');

      this._handleMarkersZooming($item.data('id'));
      this._handleHighlightedItemScroll($item, $container);
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

      this.map = new google.maps.Map(this.resultsMap[0], mapOptions);
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
      this.resultsMap = $(this.el);
      this.findLegalAdviserContainer = $('.find-legal-adviser');
      this.organisationListItems = $('.search-results-list .vcard');
    }
  };
}());
