import React from "react";
import ReactDOM from "react-dom";
import ReactTable from 'react-table'
import {
    BrowserRouter as Router,
    Route,
    Link
} from 'react-router-dom'
import { GameDateGames } from './GameDateGames'


const RouterSidebar = () => (
    <Router>
        <div>
            <nav className={'navbar navbar-toggleable-md navbar-inverse bg-inverse'} style={{ marginBottom: '20px' }}>
                <ul className={'navbar-nav mr-auto'}>
                    <li className={'nav-item'}><Link className={'nav-link'} to="/">Home</Link></li>
                    <li className={'nav-item'}><Link className={'nav-link'} to="/gameDateGames">Game Date Games</Link></li>
                    <li className={'nav-item'}><Link className={'nav-link'} to="/players">Players</Link></li>
                </ul>
            </nav>

            <Route exact path="/" component={Home} />
            <Route path="/gameDateGames" component={GameDateGames} />
            <Route path="/players" component={Players} />
        </div>
    </Router>
)

const Home = () => (
    <div>
        <h2>Home</h2>
    </div>
)

const Players = () => (
    <div>
        <h2>Players</h2>
    </div>
)

ReactDOM.render(<RouterSidebar />, document.getElementById("content"));
