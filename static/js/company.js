// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // user data
        user_name: "",
        user_balance: 0,
        user_pfp: "",

        co_id: 0,
        co_name: "",
        co_symbol: "",
        co_price: 0,
        date: "",
        co_change: 0,
        co_pct_change: 0,
        is_green: false,
        is_red: false,
        is_flat: false,
        buy_menu: false,
        sell_menu: false,
        buy_amount: 0,
        sell_amount: 0,
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    // Determine color of price by comparing the last history elem, with the first
    app.determine_color = function(change) {
        app.vue.is_green = change > 0;
        app.vue.is_red = change < 0;
        app.vue.is_flat = change === 0;
    };
    
    // Get updated stock prices
    app.refresh_quote = function() {
    	axios.get(load_company_url, {
            params: {
                co_symbol: app.vue.co_symbol
            }
        }).then(function (response) {
            app.vue.co_price = response.data.co_price.toFixed(2);
            app.vue.co_change = response.data.co_change.toFixed(2);
            app.vue.co_pct_change = response.data.co_pct_change;
            app.vue.date = response.data.date;

            app.plot_history();
        });
    };

    app.plot_history = function() {
        axios.get(get_history_url, {
            params: {
                co_symbol: app.vue.co_symbol
            }
        }).then(function(response) {
            let stock_history = response.data.stock_history;
            let dates = response.data.dates;

            // determine color of text
            change = stock_history[stock_history.length-1] - stock_history[0];
            app.determine_color(change);
            plotter.plot_stock_history(dates, stock_history, "chart_div", app.vue.co_name);
        });
    };

    app.show_buy_menu = function(flag) {
        app.vue.buy_menu = flag;
    };

    app.show_sell_menu = function(flag) {
        app.vue.sell_menu = flag;
    };

    app.buy_shares = function() {
        axios.post(buy_shares_url,
            {
                num_shares: app.vue.buy_amount,
                co_id: app.vue.co_id,
                price: app.vue.co_price,
            }).then(function (response) {
                app.reset_form(true);
                app.show_buy_menu(false);
            });
    };

    app.sell_shares = function() {
        axios.post(sell_shares_url,
            {
                num_shares: app.vue.sell_amount,
                co_id: app.vue.co_id,
                price: app.vue.co_price,
            }).then(function (response) {
                app.reset_form(false);
                app.show_sell_menu(false);
            });
    }

    // True: buy
    // False: sell
    app.reset_form = function(flag) {
        if (flag) {
            app.vue.buy_amount = 0;
        }
        else {
            app.vue.sell_amount = 0;
        }
    }

    // This contains all the methods
    app.methods = {
        determine_color: app.determine_color,
        refresh_quote: app.refresh_quote,
        show_buy_menu: app.show_buy_menu,
        show_sell_menu: app.show_sell_menu,
        plot_history: app.plot_history,
        buy_shares: app.buy_shares,
        sell_shares: app.sell_shares,
        reset_form: app.reset_form,
    };

    // This creates the Vue instance
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    app.init = () => {
        // request user info
        axios.get(get_user_info_url).then(function (response) {
            app.vue.user_name = response.data.first_name + " " + response.data.last_name;
            app.vue.user_balance = response.data.balance;
            app.vue.user_pfp = response.data.pfp;
        });

        // split the pathname to get the company id
        let company_path = location.pathname;
        path_elems = company_path.split(/\//);
        let co_id = path_elems[path_elems.length-1];
        // If no company was provided, set the default to the
        // first company in the db
        if (co_id === "company" || co_id === "") {
            co_id = -1;
        }
        // Get the company information
        axios.get(load_company_url, {
            params: {
                co_id: co_id
            }
        }).then(function (response) {
            app.vue.co_id = response.data.co_id;
            app.vue.co_name = response.data.co_name;
            app.vue.co_symbol = response.data.co_symbol;
            app.vue.co_price = response.data.co_price.toFixed(2);
            app.vue.date = response.data.date;
            app.vue.co_change = response.data.co_change.toFixed(2);
            app.vue.co_pct_change = response.data.co_pct_change.toFixed(2);

            // plot graph of company history
            google.charts.setOnLoadCallback(app.plot_history);
        });
    };

    // Call to the initializer
    app.init();
};

// Initialize plotter
let plotter = new Plotter();

// Initialize the app object
init(app);
