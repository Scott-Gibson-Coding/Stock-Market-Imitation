// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        co_name: "",
        co_ticker: "",
        co_price: 0,
        co_change: 0,
        co_pct_change: 0,
        date: "",
        is_green: false,
        is_red: false,
        is_flat: false,
        buy_menu: false,
        sell_menu: false,
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    // Determine color of price
    app.determine_color = function(change) {
        if (change > 0) {
            app.vue.is_green = true;
            app.vue.is_red = false;
            app.vue.is_flat = false;
        }
        else if (change < 0) {
            app.vue.is_green = false;
            app.vue.is_red = true;
            app.vue.is_flat = false;
        }
        else {
            app.vue.is_green = false;
            app.vue.is_red = false;
            app.vue.is_flat = true;
        }
    }

    // Get updated stock prices
    app.refresh_quote = function(co_id) {
        axios.post(company_refresh_url, {
            co_id: co_id
        }).then(function (response) {
            app.vue.co_price = response.data.companies['current_stock_value'];
        });
    };

    app.show_buy_menu = function(flag) {
        app.vue.buy_menu = flag;
    }

    app.show_sell_menu = function(flag) {
        app.vue.sell_menu = flag;
    }

    // This contains all the methods
    app.methods = {
        determine_color: app.determine_color,
        refresh_quote: app.refresh_quote,
        show_buy_menu: app.show_buy_menu,
        show_sell_menu: app.show_sell_menu,
    };

    // This creates the Vue instance
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    app.init = () => {
        // Put here any initialization code
    };

    // Call to the initializer
    app.init();
};

// Initialize the app object
init(app);