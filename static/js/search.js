// This will be the object that will contain the Vue attributes
// and be used to initialize it.
// This is in main
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        proof: "Search Proof",
        company_rows: [],
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };


    // This contains all the methods
    app.methods = {
        
    };

    // This creates the Vue instance
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    app.init = () => {
        app.vue.company_rows.push({
            company_name: "Apple",
            company_symbol: "AAPL"
        })
        console.log("init")
        console.log(app.vue.company_rows)
    };

    // Call to the initializer
    app.init();
};
console.log("startup")
// Initialize the app object
init(app);
