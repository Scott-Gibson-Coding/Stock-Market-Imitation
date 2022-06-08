// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        status : "",
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.do_action = function(action) {
        axios.post(admin_url, {
            action : action
        }).then(function(r) {
            app.vue.status = 'Dumped transactions table'
        });
    };

    // This contains all the methods
    app.methods = {
        do_action : app.do_action,
    };

    // This creates the Vue instance
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    app.init = () => {

    };

    // Call to the initializer
    app.init();
};

// Initialize the app object
init(app);