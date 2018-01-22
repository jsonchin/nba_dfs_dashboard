import React from "react";
import ReactDOM from "react-dom";
import ReactTable from 'react-table'
import {
    BrowserRouter as Router,
    Route,
    Link
} from 'react-router-dom'
import { GameDateGames } from './GameDateGames'
import { GameDayAnalysis } from './GameDayAnalysis/GameDayAnalysis'


const RouterSidebar = () => (
    <Router>
        <div>
            <nav className={'navbar navbar-toggleable-md navbar-inverse bg-inverse'} style={{ marginBottom: '20px' }}>
                <ul className={'navbar-nav mr-auto'}>
                    <li className={'nav-item'}><Link className={'nav-link'} to="/">Home</Link></li>
                    <li className={'nav-item'}><Link className={'nav-link'} to="/gameDateGames">Previous Games</Link></li>
                    <li className={'nav-item'}><Link className={'nav-link'} to="/gameDayAnalysis">Game Day Analysis</Link></li>
                </ul>
            </nav>

            <Route exact path="/" component={Home} />
            <Route path="/gameDateGames" component={GameDateGames} />
            <Route path="/gameDayAnalysis" component={GameDayAnalysis} />
        </div>
    </Router>
)

const Home = () => (
    <h2>Home</h2>
)

ReactDOM.render(<RouterSidebar />, document.getElementById("content"));
