// Import Plotter
import {Plotter} from "./Plotter.js";

// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {

    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.plot_history = function(){
        // Get stock values of the first company (test)
        axios.get(get_history_url).then(function(response){
            let company_name = response.data.name;
            let stock_history = response.data.stock_history;
            let dates = response.data.dates;
            plotter.plot_stock_history(dates, stock_history, "chart_div", company_name);
        });
    }

    // This contains all the methods
    app.methods = {
        plot_history : app.plot_history,
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
// Initialize plotter
let plotter = new Plotter();

// Initialize the app object
init(app);