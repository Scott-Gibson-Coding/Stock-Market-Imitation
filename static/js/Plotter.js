// Class to house plotting functionality
class Plotter{
    // Constructor
    constructor(){
        /**
         * Plotting utility which uses the Google Charts API.
         */
        // Connect to google chart script
        let script = document.createElement('script');
        document.head.appendChild(script);
        script.onload = function(){
            // Load google chart packages
            google.charts.load('current', {'packages':['corechart']});
            //google.charts.setOnLoadCallback();
        }
        script.src = 'https://www.gstatic.com/charts/loader.js'
    }

    // Methods
    generate_table(data, dates){
        let table = new google.visualization.DataTable();
        // Add columns to the table
        table.addColumn('datetime', 'Date');
        table.addColumn('number', 'Value');
        // Rows
        table.addRows(data.length);
        for (let i = 0; i < data.length; i++){
            // Time
            table.setCell(i, 0, new Date(dates[i]));
            // Value
            table.setCell(i, 1, data[i]);
        }
        return table
    }

    plot_stock_history(dates, hist, div_id, title=""){
        if (hist.length != dates.length){
            console.error("Number of dates must equal number of values.");
            return null;
        }
        let data = this.generate_table(hist, dates);
        let doc_element = document.getElementById(div_id);
        if (doc_element === null){
            console.error("HTML element with id \"" + div_id + "\" cannot be found.");
            return null;
        }
        // Hook the chart to the div_id element
        let chart = new google.visualization.LineChart(doc_element);
        // Set up options
        let first_val = data.getValue(0, 1);
        let last_val = data.getValue(data.getNumberOfRows()-1, 1);
        // If value has increased, plot green line, else red
        let color = "";
        if (last_val > first_val){
            color = 'green';
        }else if (last_val === first_val){
            color='blue';
        }else{
            color='red';
        }
        let options = {
            title: title,
            colors: [color],
            hAxis : {
                title: "Date",
                //format: 'MMM d, hh:mm:ss',
                format: 'M/d/yy',
                gridlines:{
                    count: 5,
                },
            },
            vAxis : {
                title: "Value",
            },
            trendlines : {
                0:{
                    type: 'linear',
                    color: 'black',
                    lineWidth: 3,
                    opacity: 0.3,
                    visibleInLegend: true,
                    labelInLegend: "Trend",
                }
            }
        }
        // Draw the chart
        chart.draw(data, options);
    }
}