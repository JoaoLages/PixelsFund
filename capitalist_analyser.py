import plotly
import plotly.graph_objs as go
from utils import read_json
import numpy as np
import pandas as pd

while True:
    transactions = read_json('transactions.json')
    projects_json = read_json('projects.json')
    wallet2user = read_json('wallet2user.json')

    projects_wallets_to_ids = dict()
    projects_wallets_to_project_json = dict()
    projects_wallets = set()
    for x in projects_json:
        projects_wallets_to_ids["0x%s" % x['wallet']] = x['id']
        projects_wallets_to_project_json["0x%s" % x['wallet']] = x
        projects_wallets |= {"0x%s" % x['wallet']}

    user2balance = dict()
    for wallet in wallet2user:
        if all(x in wallet2user[wallet] for x in ['balance', 'user']):
            user2balance[wallet2user[wallet]['user']] = wallet2user[wallet]['balance']
        elif 'user' in wallet2user[wallet]:  # No EXP
            user2balance[wallet2user[wallet]['user']] = 0
        else:
            pass

    investors = []
    projects = []
    timestamps = []
    EXP_invested = []
    for investor in transactions['from_to_amount']:
        for potential_project in transactions['from_to_amount'][investor]:
            if potential_project in projects_wallets:
                # Is a project
                for investment in transactions['from_to_amount'][investor][potential_project]:
                    investors.append(investor)
                    projects.append(potential_project)
                    timestamps.append(investment['timestamp'])
                    EXP_invested.append(investment['balance'])

    # Investors wallets, projects wallets, TIMESTAMPS, EXP
    sorted_investments = sorted(zip(investors, projects, timestamps, EXP_invested), key= lambda x: x[2])

    # Graphs and table
    graph1 = []
    table1 = []
    index1 = []
    investors2balance = {}  # Stores investor's EXP left
    projects_members2balance = {}  # Stores sum of project's members EXP left

    N = len(list(set(investors)))
    c = ['hsl(' + str(h) + ',50%' + ',50%)' for h in np.linspace(0, 360, N)]
    for i, investor in enumerate(list(set(investors))):
        if investor in wallet2user and 'user' in wallet2user[investor]:
            investor_name = wallet2user[investor]['user']
        else:
            investor_name = investor

        # Save investors' EXP left
        investors2balance[investor] = wallet2user[investor]['balance']

        invests = [t for t in sorted_investments if t[0] == investor]
        invests_projects = list({t[1] for t in invests})

        for project in projects_wallets:
            if project in projects_wallets_to_ids:
                project_name = projects_wallets_to_ids[project]
            else:
                project_name = project

            # Save Project member's EXP left
            project_members_usernames = [x['user'] for x in projects_wallets_to_project_json[project]['users']
                                         if x['user'] in user2balance]
            projects_members2balance[project] = sum([user2balance[x] for x in project_members_usernames])

            if project in invests_projects:
                x_axis = [t[2] for t in sorted_investments if t[0] == investor and t[1] == project and t[3] > 10]
                y_axis = [t[3] for t in sorted_investments if t[0] == investor and t[1] == project and t[3] > 10]
                if x_axis:
                    graph1.append(
                        plotly.graph_objs.Scatter(
                            x=x_axis,
                            y=y_axis,
                            name='%s, Project_%s' % (investor_name, project_name),
                            marker=dict(color=c[i])
                        )
                    )

        # Append investor name
        index1.append(investor_name)

        # Get total balance and invested
        EXP_balance = wallet2user[investor]['balance']
        EXP_invested = sum([t[3] for t in sorted_investments if t[0] == investor])

        table1.append([EXP_balance, EXP_invested])

    # Sort table by balance
    sorted_table = sorted(zip(table1, index1), key=lambda x: x[0][0])[::-1]
    table1 = []
    index1 = []
    for x in sorted_table:
        table1.append(x[0])
        index1.append(x[1])

    graph2 = []
    project_names = []
    project_balances = []
    project_investor_funds_left = []
    project_member_funds_left = []

    N = len(list(projects_wallets))
    c = ['hsl(' + str(h) + ',50%' + ',50%)' for h in np.linspace(0, 360, N)]
    for i, project in enumerate(list(projects_wallets)):
        if project in projects_wallets_to_ids:
            project_name = projects_wallets_to_ids[project]
        else:
            project_name = project

        x_axis = [t[2] for t in sorted_investments if t[1] == project]
        y_axis = [t[3] for t in sorted_investments if t[1] == project]
        y_axis = [sum(y_axis[:p + 1]) for p, y in enumerate(y_axis)]

        # Add to Project chart
        # Name
        project_names.append("Project_%s" % project_name)
        # Balance
        if y_axis:
            project_balances.append(y_axis[-1])
        else:
            project_balances.append(0)  # No investment
        # Investors + Project Members EXP left
        project_investor_funds_left.append(
            sum([investors2balance[x] for x in [t[0] for t in sorted_investments if t[1] == project]])
        )
        project_member_funds_left.append(
            projects_members2balance[project]
        )

        if x_axis and y_axis[-1] > 10:
            graph2.append(
                go.Scatter(
                    x=x_axis,
                    y=y_axis,
                    name='Project_%s' % (project_name),
                    marker=dict(color=c[i])
                )
            )

    # Top EXP left table
    balances_users = [(wallet2user[x]['balance'], wallet2user[x]['user']) for x in wallet2user
                      if all(y in wallet2user[x] for y in ['user', 'balance'])]
    # Pick top 20
    sorted_balances_users = sorted(balances_users, key=lambda x: x[0])[::-1][:20]
    table2 = [x[0] for x in sorted_balances_users]
    index2 = [x[1] for x in sorted_balances_users]
    # Add total
    table2.append(sum(table2))
    index2.append('TOTAL')

    # Projects chart
    # Sort
    sorted_projects_chart = sorted(
        zip(project_names, project_balances, project_investor_funds_left, project_member_funds_left),
        key=lambda x: int(x[0].replace('Project_', ''))
    )

    projects_chart = [
        go.Bar(
            x=list(map(lambda x: x[0], sorted_projects_chart)),
            y=list(map(lambda x: x[1], sorted_projects_chart)),
            name='Project EXP Funding'
        ),
        go.Scatter(
            x=list(map(lambda x: x[0], sorted_projects_chart)),
            y=list(map(lambda x: x[2], sorted_projects_chart)),
            name="Project's Investors EXP left",
            yaxis='y2'
        ),
        go.Scatter(
            x=list(map(lambda x: x[0], sorted_projects_chart)),
            y=list(map(lambda x: x[3], sorted_projects_chart)),
            name="Project's Members EXP left",
            yaxis='y3'
        )
    ]

    layout = go.Layout(
        title='EXP invested by each investor over time (per project) (from TOP investors)',
        xaxis={'title' : 'Time'},
        yaxis={'title' : 'EXP'}
    )
    fig = go.Figure(
        data=graph1,
        layout=layout
    )
    plotly.offline.plot(fig)

    layout = go.Layout(
        title='Total EXP invested in each Project over time (> 10EXP)',
        xaxis={'title' : 'Time'},
        yaxis={'title' : 'EXP'}
    )
    fig = go.Figure(
        data=graph2,
        layout=layout
    )
    plotly.offline.plot(fig)

    print("Top Investors (EXP Balance and Invested)")
    pd.DataFrame(
        data=table1,
        index = index1,
        columns=['EXP Balance', 'EXP Invested']
    )

    print("Top 20 Balances")
    pd.DataFrame(
        data=table2,
        index = index2,
        columns=['EXP Balance']
    )

    layout = go.Layout(
        title='Projects Analysis',
        yaxis=dict(
            title='Project EXP funding'
        ),
        yaxis2=dict(
            title="EXP left to Invest",
            titlefont=dict(
                color='#ff7f0e'
            ),
            tickfont=dict(
                color='#ff7f0e'
            ),
            anchor='x',
            overlaying='y',
            side='right',
            range=[1000, 100000]
        ),
        yaxis3=dict(
            tickfont=dict(
                color='#d62728'
            ),
            anchor='x',
            overlaying='y',
            side='right',
            range=[1000, 100000]
        ),

    )
    fig = go.Figure(
        data=projects_chart,
        layout=layout
    )
    plotly.offline.plot(fig)

    import time; time.sleep(300000)