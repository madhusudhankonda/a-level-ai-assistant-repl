window.addEventListener('DOMContentLoaded', function() {
    // Configure MathJax
    window.MathJax = {
        tex: {
            inlineMath: [['$', '$'], ['\\(', '\\)']],
            displayMath: [['$$', '$$'], ['\\[', '\\]']],
            processEscapes: true,
            processEnvironments: true
        },
        options: {
            enableMenu: false,
            processSectionDelay: 0
        },
        startup: {
            pageReady: function() {
                return MathJax.startup.defaultPageReady().then(function() {
                    console.log('MathJax initial typesetting complete');
                });
            }
        }
    };

    // Function to render math in a specific element
    window.renderMathInElement = function(element) {
        if (typeof MathJax !== 'undefined' && MathJax.typesetPromise) {
            MathJax.typesetPromise([element]).then(function() {
                console.log('MathJax typesetting complete for element');
            }).catch(function(err) {
                console.error('MathJax typesetting failed:', err);
            });
        } else {
            console.error('MathJax not loaded properly');
        }
    };
});
