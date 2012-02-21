(function(jQuery) {
  "use strict";
  
  var $ = jQuery;
  
  function normalizeLanguage(language) {
    var match = language.match(/([A-Za-z]+)-([A-Za-z]+)/);
    if (match)
      return match[1].toLowerCase() + "-" + match[2].toUpperCase();
    return language.toLowerCase();
  }

  function indexOfNearMatch(locale, available) {
    var match;
    if (locale.indexOf('-') != -1) {
      var localeParts = locale.split('-');
      match = jQuery.inArray(localeParts[0], available);
    }
    else {
      match = jQuery.inArray(locale, jQuery.map(available, function(locale){ 
        var localeParts = locale.split('-');
        return localeParts[0];
      }));
    }
    return match;
  }
   

  jQuery.extend({
    localization: {
      DEFAULT: "en-US",
      activateBestLocale: function(path) {
        var div = $("<div></div>");
        div.load("/" + this.DEFAULT + "/language-selector.html", function() {
          var available = [];
          $(this).find("option").each(function() {
            available.push(this.value);
          });
          var language = navigator.language || navigator.userLanguage;
          var bestMatch = jQuery.localization.findBestMatch(language,
                                                            available);
          jQuery.localization.activate(bestMatch, true, path);
        });
      },
      findBestMatch: function(locale, available) {
        locale = normalizeLanguage(locale);
        if (jQuery.inArray(locale, available) != -1){
          return locale;
        }
        else {
          var nearMatch = indexOfNearMatch(locale, available);
          if (nearMatch == -1) {
            return this.DEFAULT;
          }
          return available[nearMatch];
        }
      },
      activate: function(locale, replaceState, path) {
        var newURL = '/' + locale + (path || '/');
        if (replaceState && window.history && window.history.replaceState) {
          window.history.replaceState({}, "", newURL);
          window.location.reload();
        } else
          window.location = newURL;
      }
    }
  });
  
  $("select.language-selector").live("change", function() {
    jQuery.localization.activate(this.options[this.selectedIndex].value);
  });
})(jQuery);
