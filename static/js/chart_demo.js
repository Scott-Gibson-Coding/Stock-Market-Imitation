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
            company_name = response.data.name;
            stock_history = response.data.stock_history;
            // Hook a google linechart to the chart_div element
            let chart = new google.visualization.LineChart(document.getElementById('chart_div'));
            // Create a google data table to plot in the line chart
            let data = new google.visualization.DataTable();
            // Columns
            data.addColumn('number', 'Time');
            data.addColumn('number', 'Value');
            // Rows
            data.addRows(stock_history.length);
            for (let i = 0; i < stock_history.length; i++){
                data.setCell(i, 0, i);
                data.setCell(i, 1, stock_history[i]);
            }
            let options = {
                title: 'Stock History for ' + company_name,
            };
            // Draw the chart
            chart.draw(data, options);
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

// Initialize the app object
init(app);

// Load google chart packages
google.charts.load('current', {'packages':['corechart']});
// One loaded, plot the initial history
google.charts.setOnLoadCallback(app.plot_history);