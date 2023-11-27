function fetchDataAndPopulateTable() {
    $.get("https://api.coingecko.com/api/v3/coins/markets?x_cg_demo_api_key=CG-KoDWqDuHCWkxgES3WWTuZtBT&vs_currency=usd&order=market_cap_desc&per_page=20&page=1&sparkline=false&locale=en", function (data) {
        // Assuming the API returns JSON data
        // You can now store, process, or display the data
        console.log(data); // Log the data to the console for demonstration

        // Example: Store the data in a variable
        var items = data;

        // You can now work with 'items' as needed
        // For example, you can access properties like items.propertyName

        // Clear existing table rows
        $('table tbody').empty();

        // Populate the table with data
        items.forEach((data, index) => {
            const $row = $('<tr>');
            $row.append(`<td>${index + 1}</td>`);

            // Add the coin symbol image and name in the "Coin" column
            const $coinCell = $('<td>');
            const $coinImage = $('<img>');
            $coinImage.attr('src', data.image);
            // $coinImage.attr('alt', data.symbol);
            $coinImage.attr('width', '30px');
            $coinImage.attr('height', '30px');
            $coinCell.append($coinImage);
            $coinCell.append(data.symbol);
            $row.append($coinCell);

            $row.append(`<td>${data.current_price}</td>`);
            $row.append(`<td>${data.price_change_percentage_24h}</td>`);
            $row.append(`<td>${data.total_volume}</td>`);
            $row.append(`<td>${data.market_cap}</td>`);

            $('table tbody').append($row);
        });
    });
}

$(document).ready(function () {
    fetchDataAndPopulateTable(); // Initial data fetch and population
});
