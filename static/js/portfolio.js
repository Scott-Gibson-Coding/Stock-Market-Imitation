// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        holdings : [],
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.get_holdings = function() {
        axios.post(get_holdings_url, {}).then(function(r) {
            app.vue.holdings = r.data.holdings;
        });
    }

    app.to_company = function(ticker) {
        window.location.href = "../company/" + ticker;
    }

    // This contains all the methods
    app.methods = {
        get_holdings : app.get_holdings,
        to_company : app.to_company,
    };

    // This creates the Vue instance
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    app.init = () => {
        app.get_holdings();
    };

    // Call to the initializer
    app.init();
};

// Initialize the app object
init(app);