angular.module('directives', [])

  .directive('glyptoModel', function($compile, $http, $templateCache) {
    return {
      restrict: 'C',
      scope: true
    };
  })

  .directive('glyptoNavToggle', function() {
    return {
      restrict: 'C',
      link: function($scope, $element, $attrs) {
        $scope.hidden = store.get('glypto-menu-hidden');

        Mousetrap.bind('command+shift+e', function() {
          $scope.toggle();
          $scope.$apply();
        });

        $scope.toggle = function() {
          $scope.hidden = !$scope.hidden;
          store.set('glypto-menu-hidden', $scope.hidden);
        };
      }
    };
  })

  .directive('glyptoMenu', function() {
    return {
      restrict: 'E',
      replace: true,
      scope: true,
      templateUrl: 'glyptotheque/menu.html',
      controller: function($scope) {
        $scope.items = window.APP_CONTEXT.sitemap;
      },
      link: function() {
        // Remove nav placeholder when menu is created
        angular.element(document.getElementById('glypto-nav-placeholder')).remove();
      }
    };
  })

  .directive('glyptoMenuTree', function() {
    return {
      restrict: 'E',
      replace: true,
      transclude: true,
      scope: {
        items: '=',
        filter: '='
      },
      templateUrl: 'glyptotheque/menu-tree.html'
    };
  })

  .directive('glyptoMenuNode', function($compile) {
    return {
      restrict: 'E',
      replace: true,
      templateUrl: 'glyptotheque/menu-node.html',
      link: function($scope, $element, $attrs) {
        $scope.isSelected = $scope.node.url === window.APP_CONTEXT.current_url;

        if ($scope.node.children && $scope.node.children.length > 0) {
          var childNode = $compile('<glypto-menu-tree items="node.children" filter="filter"></glypto-menu-tree>')($scope);
          $element.append(childNode);
        }
      }
    };
  })

  .directive('glyptoSearch', function() {
    return {
      restrict: 'A',
      link: function($scope, $element, $attrs) {
        var activated;
        var placeholderText = $element.attr('placeholder');

        Mousetrap.bind('/', function(evt) {
          if(!activated) {
            evt.preventDefault();
          }
          $element[0].focus();
          $element.attr('placeholder', placeholderText.replace(/\(.*\)/, ''));
        });

        Mousetrap.bind('esc', function(evt) {
          if(!activated) {
            evt.preventDefault();
          }
          $element[0].blur();
          $element.attr('placeholder', placeholderText);
        });

        $element.on('focus', function() {
          activated = true;
        });

        $element.on('blur', function() {
          activated = false;
        });
      }
    };
  });
