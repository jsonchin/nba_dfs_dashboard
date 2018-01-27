import React from "react";
import ReactTable from 'react-table'
import { mapMultipleRowsToCol, constructReactTableColumns } from './utils'


const COLUMN_WIDTHS = {
    'MIN': 40
};

const PLAYER_AVERAGES_STYLE = {
    width: '100%',
    fontSize: '12px',
    textAlign: 'center'
};

const MAX_LOGS_PER_PAGE = 1;

export class PlayerAverages extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            error: null,
            isLoaded: false,
            data: null
        };

        fetch('/player/' + this.props.playerId + '/averages')
            .then((res) => res.json())
            .then((result) => {
                this.setState({
                    isLoaded: true,
                    data: result
                });
            },
            (error) => {
                this.setState({
                    isLoaded: true,
                    error: error
                });
            });
    }

    render() {
        const { error, isLoaded } = this.state;
        if (error) {
            return <div>Error: {error.message}</div>;
        } else if (!isLoaded) {
            return <div>Loading...</div>;
        } else {
            const columnNames = ['DK_FP', 'MIN', 'PTS', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'DD2', 'TD3', 'FGM', 'FG_PCT', 'FG3M', 'FG3_PCT', 'PLUS_MINUS'];
            const rows = [this.state.data.averages];
            const columns = constructReactTableColumns(columnNames, COLUMN_WIDTHS);

            return (<ReactTable
                className={'-striped -highlight'}
                data={rows}
                columns={columns}
                sortable={false}
                resizable={false}
                showPagination={false}
                showPageJump={false}
                defaultPageSize={MAX_LOGS_PER_PAGE}
                style={PLAYER_AVERAGES_STYLE}
            />);
        }
    }
}