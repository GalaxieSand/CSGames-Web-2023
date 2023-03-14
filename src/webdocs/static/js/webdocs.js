    var markdownContent = {
      "en": "",
      "fr": ""
    };
    var contentUrl = {
      "fr": "enonce_dist.md",
      "en": "tasks_dist.md"
    }

    function showMarkdown(lang) {
      if(markdownContent[lang].length == 0)
      {
          $.ajax({
            url: contentUrl[lang],
            success: function( result ) {
              result = result.replace(/</g, "&lt;");
              result = result.replace(/>/g, "&gt;");
              markdownContent[lang] = result;
              document.getElementById('content').innerHTML = marked.parse(result);
              }
            });
      }
      else
      {
        document.getElementById('content').innerHTML = marked.parse(markdownContent[lang]);
      }
    }

    function loadWithLocale() {
        if (navigator.languages != undefined) {
            var lang = navigator.languages[0];
            if(lang.startsWith('en')) {
                showMarkdown('en')
            } else if(lang.startsWith('fr')) {
                showMarkdown('fr')
            }
        }
    }
