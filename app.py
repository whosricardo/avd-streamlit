import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from src.data_loader import load_data


st.set_page_config(
    page_title="LoL aos 10 minutos — análise de partidas",
    page_icon="⚔️",
    layout="wide",
)

GREEN_DARK = "#0f5132"
GREEN = "#1b7f5a"
AMBER = "#d99a16"

VARS_QUANT = [
    "blueWardsPlaced", "blueWardsDestroyed", "blueKills", "blueDeaths",
    "blueAssists", "blueEliteMonsters", "blueTotalGold", "blueAvgLevel",
    "blueTotalExperience", "blueTotalMinionsKilled",
    "blueTotalJungleMinionsKilled", "blueGoldDiff", "blueExperienceDiff",
    "blueCSPerMin", "blueGoldPerMin", "redWardsPlaced",
    "redWardsDestroyed", "redKills", "redDeaths", "redAssists",
    "redEliteMonsters", "redTotalGold", "redAvgLevel",
    "redTotalExperience", "redTotalMinionsKilled",
    "redTotalJungleMinionsKilled", "redGoldDiff", "redExperienceDiff",
    "redCSPerMin", "redGoldPerMin",
]

LABELS = {
    "blueWardsPlaced": "Wards colocadas — Azul",
    "blueWardsDestroyed": "Wards destruídas — Azul",
    "blueKills": "Abates — Azul",
    "blueDeaths": "Mortes — Azul",
    "blueAssists": "Assistências — Azul",
    "blueEliteMonsters": "Monstros épicos — Azul",
    "blueTotalGold": "Ouro total — Azul",
    "blueAvgLevel": "Nível médio — Azul",
    "blueTotalExperience": "Experiência total — Azul",
    "blueTotalMinionsKilled": "Minions abatidos — Azul",
    "blueTotalJungleMinionsKilled": "Monstros da selva — Azul",
    "blueGoldDiff": "Diferença de ouro (Azul − Vermelho)",
    "blueExperienceDiff": "Diferença de XP (Azul − Vermelho)",
    "blueCSPerMin": "CS por minuto — Azul",
    "blueGoldPerMin": "Ouro por minuto — Azul",
    "redWardsPlaced": "Wards colocadas — Vermelho",
    "redWardsDestroyed": "Wards destruídas — Vermelho",
    "redKills": "Abates — Vermelho",
    "redDeaths": "Mortes — Vermelho",
    "redAssists": "Assistências — Vermelho",
    "redEliteMonsters": "Monstros épicos — Vermelho",
    "redTotalGold": "Ouro total — Vermelho",
    "redAvgLevel": "Nível médio — Vermelho",
    "redTotalExperience": "Experiência total — Vermelho",
    "redTotalMinionsKilled": "Minions abatidos — Vermelho",
    "redTotalJungleMinionsKilled": "Monstros da selva — Vermelho",
    "redGoldDiff": "Diferença de ouro — Vermelho",
    "redExperienceDiff": "Diferença de XP — Vermelho",
    "redCSPerMin": "CS por minuto — Vermelho",
    "redGoldPerMin": "Ouro por minuto — Vermelho",
}

DEFAULT_VARS = [
    "blueKills", "blueTotalGold", "blueAvgLevel", "blueTotalExperience",
    "blueGoldDiff", "blueExperienceDiff",
]

WINNER_SCALE = alt.Scale(
    domain=["Time Azul", "Time Vermelho"],
    range=[GREEN, AMBER],
)


def prepare_data(data: pd.DataFrame) -> pd.DataFrame:
    """Valida a exportação do notebook e cria campos derivados se necessário."""
    required = {"gameId", "blueWins", *VARS_QUANT}
    missing = sorted(required.difference(data.columns))
    if missing:
        st.error(
            "O arquivo `data/clean/dataset.csv` ainda não é a exportação da EDA de "
            "League of Legends. Execute todas as células de "
            "`notebooks/eda-com-downloads.ipynb` para regenerá-lo."
        )
        with st.expander("Colunas de LoL ausentes"):
            st.code("\n".join(missing))
        st.stop()

    prepared = data.copy()
    if "team_label" not in prepared:
        prepared["team_label"] = prepared["blueWins"].map(
            {0: "Time Vermelho", 1: "Time Azul"}
        )
    if "avg_level_band" not in prepared:
        prepared["avg_level_band"] = pd.cut(
            prepared["blueAvgLevel"],
            bins=[-np.inf, 6.8, 7.0, 7.2, np.inf],
            labels=["Baixo", "Médio-baixo", "Médio-alto", "Alto"],
        )
    if "blueObjectives" not in prepared:
        prepared["blueObjectives"] = (
            prepared["blueDragons"]
            + prepared["blueHeralds"]
            + prepared["blueTowersDestroyed"]
        )
    if "redObjectives" not in prepared:
        prepared["redObjectives"] = (
            prepared["redDragons"]
            + prepared["redHeralds"]
            + prepared["redTowersDestroyed"]
        )
    return prepared


@st.cache_data
def aggregate_histogram(
    data: pd.DataFrame, column: str, split_by_winner: bool, bins: int = 28
) -> pd.DataFrame:
    """Agrega o histograma antes de enviá-lo ao Altair."""
    values = data[column].dropna()
    if values.empty:
        return pd.DataFrame()

    edges = np.linspace(float(values.min()), float(values.max()), bins + 1)
    if edges[0] == edges[-1]:
        edges[-1] = edges[0] + 1.0

    valid = data[[column, "team_label"]].dropna().copy()
    indexes = np.clip(np.digitize(valid[column], edges, right=True) - 1, 0, bins - 1)
    histogram = pd.DataFrame(
        {
            "bin_start": edges[indexes],
            "bin_end": edges[indexes + 1],
            "team_label": valid["team_label"].to_numpy(),
        }
    )
    group_columns = ["bin_start", "bin_end"]
    if split_by_winner:
        group_columns.append("team_label")
    return (
        histogram.groupby(group_columns, as_index=False, observed=True)
        .size()
        .rename(columns={"size": "matches"})
    )


st.title("League of Legends aos 10 minutos")
st.caption(
    "Como as vantagens construídas no início da partida se relacionam com o vencedor "
    "em jogos ranqueados Diamond/Master?"
)

df = prepare_data(load_data())

with st.sidebar:
    st.header("Recorte da análise")
    variables = st.multiselect(
        "Variáveis quantitativas",
        options=VARS_QUANT,
        default=DEFAULT_VARS,
        format_func=lambda value: LABELS[value],
        help="As variáveis seguem a seleção quantitativa do notebook de EDA.",
    )
    split_by_winner = st.toggle(
        "Separar pelo vencedor",
        value=True,
        help="Compara partidas vencidas pelos times azul e vermelho.",
    )

    st.subheader("Intervalos")
    intervals: dict[str, tuple[float, float]] = {}
    for variable in variables:
        series = df[variable].dropna()
        if pd.api.types.is_integer_dtype(series):
            minimum, maximum, step = int(series.min()), int(series.max()), 1
        else:
            minimum, maximum, step = float(series.min()), float(series.max()), 0.1
        intervals[variable] = st.slider(
            LABELS[variable],
            min_value=minimum,
            max_value=maximum,
            value=(minimum, maximum),
            step=step,
            key=f"range_{variable}",
        )

df_filtered = df
for variable, (start, end) in intervals.items():
    df_filtered = df_filtered[df_filtered[variable].between(start, end)]

st.caption(
    f"{len(df_filtered):,} de {len(df):,} partidas no recorte atual.".replace(",", ".")
)

tab_dashboard_1, tab_dashboard_2 = st.tabs(
    ["Dashboard 1 · Relações", "Dashboard 2 · Desempenho"]
)

with tab_dashboard_1:
    correlation_column, distribution_column = st.columns([1.15, 1], gap="large")

    with correlation_column:
        st.subheader("Correlação de Spearman")
        st.caption("O triângulo inferior evita repetir pares equivalentes.")

        if len(variables) < 2:
            st.warning("Selecione ao menos duas variáveis para calcular a correlação.")
        elif len(df_filtered) < 30:
            st.warning("O recorte precisa ter ao menos 30 partidas para esta visualização.")
        else:
            correlation = (
                df_filtered[variables]
                .corr(method="spearman")
                .rename_axis(index="variable_y", columns="variable_x")
                .stack()
                .rename("correlation")
                .reset_index()
            )
            order = {variable: index for index, variable in enumerate(variables)}
            correlation = correlation[
                correlation["variable_y"].map(order)
                > correlation["variable_x"].map(order)
            ].copy()
            correlation["label_x"] = correlation["variable_x"].map(LABELS)
            correlation["label_y"] = correlation["variable_y"].map(LABELS)

            base = alt.Chart(correlation).encode(
                x=alt.X(
                    "label_x:N", title=None,
                    sort=[LABELS[value] for value in variables[:-1]],
                    axis=alt.Axis(labelAngle=-35, labelLimit=140),
                ),
                y=alt.Y(
                    "label_y:N", title=None,
                    sort=[LABELS[value] for value in variables[1:]],
                    axis=alt.Axis(labelLimit=170),
                ),
            )
            cells = base.mark_rect(cornerRadius=3).encode(
                color=alt.Color(
                    "correlation:Q", title="Spearman (r)",
                    scale=alt.Scale(
                        domain=[-1, 0, 1], range=[AMBER, "#f6f4e9", GREEN_DARK]
                    ),
                ),
                tooltip=[
                    alt.Tooltip("label_y:N", title="Variável Y"),
                    alt.Tooltip("label_x:N", title="Variável X"),
                    alt.Tooltip("correlation:Q", title="Correlação", format=".2f"),
                ],
            )
            labels = base.mark_text(fontSize=12, fontWeight=600).encode(
                text=alt.Text("correlation:Q", format=".2f"),
                color=alt.condition(
                    "abs(datum.correlation) >= 0.55",
                    alt.value("white"), alt.value("#24332b"),
                ),
            )
            st.altair_chart((cells + labels).properties(height=480), width="stretch")

    with distribution_column:
        st.subheader("Distribuição")
        st.caption("Compare o comportamento da variável no recorte selecionado.")

        if not variables:
            st.warning("Selecione uma variável para exibir sua distribuição.")
        elif df_filtered.empty:
            st.warning("Nenhuma partida corresponde aos intervalos escolhidos.")
        else:
            histogram_variable = st.selectbox(
                "Variável do histograma", options=variables,
                index=len(variables) - 1,
                format_func=lambda value: LABELS[value],
            )
            histogram_data = aggregate_histogram(
                df_filtered, histogram_variable, split_by_winner
            )
            histogram = (
                alt.Chart(histogram_data)
                .mark_bar(opacity=0.88)
                .encode(
                    x=alt.X(
                        "bin_start:Q", bin="binned",
                        title=LABELS[histogram_variable],
                    ),
                    x2="bin_end:Q",
                    y=alt.Y("matches:Q", title="Partidas"),
                )
                .properties(height=440)
            )
            if split_by_winner:
                histogram = histogram.encode(
                    color=alt.Color(
                        "team_label:N", title="Vencedor", scale=WINNER_SCALE
                    ),
                    xOffset="team_label:N",
                    tooltip=[
                        alt.Tooltip("team_label:N", title="Vencedor"),
                        alt.Tooltip("bin_start:Q", title="De", format=".1f"),
                        alt.Tooltip("bin_end:Q", title="Até", format=".1f"),
                        alt.Tooltip("matches:Q", title="Partidas", format=","),
                    ],
                )
            else:
                histogram = histogram.mark_bar(color=GREEN, opacity=0.88).encode(
                    tooltip=[
                        alt.Tooltip("bin_start:Q", title="De", format=".1f"),
                        alt.Tooltip("bin_end:Q", title="Até", format=".1f"),
                        alt.Tooltip("matches:Q", title="Partidas", format=","),
                    ]
                )
            st.altair_chart(histogram, width="stretch")

with tab_dashboard_2:
    st.subheader("Vantagem construída aos 10 minutos")
    st.caption(
        "Filtre o cenário e clique em uma faixa de nível para recalcular os KPIs "
        "e o gráfico de objetivos."
    )

    filter_winner, filter_first_blood, filter_level = st.columns([1.1, 1, 1.4])
    with filter_winner:
        selected_winners = st.multiselect(
            "Vencedor da partida",
            options=["Time Azul", "Time Vermelho"],
            default=["Time Azul", "Time Vermelho"],
            key="performance_winner",
        )
    with filter_first_blood:
        selected_first_blood = st.selectbox(
            "Primeiro abate",
            options=["Qualquer time", "Time Azul", "Time Vermelho"],
            key="performance_first_blood",
        )
    with filter_level:
        level_order = ["Baixo", "Médio-baixo", "Médio-alto", "Alto"]
        available_levels = [
            level
            for level in level_order
            if level in df_filtered["avg_level_band"].dropna().astype(str).unique()
        ]
        selected_levels = st.multiselect(
            "Nível médio do time azul",
            options=available_levels,
            default=available_levels,
            key="performance_level",
        )

    performance = df_filtered[
        df_filtered["team_label"].isin(selected_winners)
        & df_filtered["avg_level_band"].astype(str).isin(selected_levels)
    ].copy()
    if selected_first_blood == "Time Azul":
        performance = performance[performance["blueFirstBlood"] == 1]
    elif selected_first_blood == "Time Vermelho":
        performance = performance[performance["blueFirstBlood"] == 0]

    if performance.empty:
        st.warning("Nenhuma partida corresponde aos filtros do Dashboard 2.")
    else:
        performance["kill_diff"] = performance["blueKills"] - performance["redKills"]
        performance["objective_diff"] = (
            performance["blueObjectives"] - performance["redObjectives"]
        )

        level_summary = (
            performance.groupby("avg_level_band", observed=True, as_index=False)
            .agg(
                matches=("gameId", "count"),
                blue_win_rate=("blueWins", lambda values: values.mean() * 100),
                average_gold_diff=("blueGoldDiff", "mean"),
                average_xp_diff=("blueExperienceDiff", "mean"),
            )
        )
        level_summary["avg_level_band"] = level_summary["avg_level_band"].astype(str)

        level_selection = alt.selection_point(
            name="level_selection",
            fields=["avg_level_band"],
        )
        level_chart = (
            alt.Chart(level_summary)
            .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
            .encode(
                x=alt.X(
                    "avg_level_band:N",
                    title="Faixa de nível médio do time azul",
                    sort=level_order,
                    axis=alt.Axis(labelAngle=0),
                ),
                y=alt.Y(
                    "blue_win_rate:Q",
                    title="Vitórias do time azul (%)",
                    scale=alt.Scale(domain=[0, 100]),
                ),
                color=alt.condition(
                    level_selection,
                    alt.value(GREEN),
                    alt.value("#d4d9d4"),
                ),
                opacity=alt.condition(
                    level_selection,
                    alt.value(1),
                    alt.value(0.55),
                ),
                tooltip=[
                    alt.Tooltip("avg_level_band:N", title="Faixa"),
                    alt.Tooltip("blue_win_rate:Q", title="Vitórias azuis", format=".1f"),
                    alt.Tooltip("average_gold_diff:Q", title="Dif. média de ouro", format="+,.0f"),
                    alt.Tooltip("average_xp_diff:Q", title="Dif. média de XP", format="+,.0f"),
                    alt.Tooltip("matches:Q", title="Partidas", format=","),
                ],
            )
            .add_params(level_selection)
            .properties(
                height=330,
                title="Taxa de vitória azul por faixa de nível médio",
            )
        )

        chart_column, objectives_column = st.columns([1, 1.15], gap="large")
        with chart_column:
            level_event = st.altair_chart(
                level_chart,
                key="level_performance_chart",
                on_select="rerun",
                width="stretch",
            )

        clicked_items = []
        if level_event and hasattr(level_event, "selection"):
            clicked_items = level_event.selection.get("level_selection", [])
        clicked_levels = [
            item["avg_level_band"]
            for item in clicked_items
            if "avg_level_band" in item
        ]
        metric_data = (
            performance[
                performance["avg_level_band"].astype(str).isin(clicked_levels)
            ]
            if clicked_levels
            else performance
        )

        if clicked_levels:
            st.info(
                f"Seleção ativa: **{', '.join(clicked_levels)}** "
                f"({len(metric_data):,} partidas). Clique fora das barras para limpar."
                .replace(",", ".")
            )

        baseline_blue_win_rate = df["blueWins"].mean() * 100
        baseline_gold_diff = df["blueGoldDiff"].mean()
        baseline_kill_diff = (df["blueKills"] - df["redKills"]).mean()
        baseline_objective_share = (
            df["blueObjectives"].sum()
            / (df["blueObjectives"].sum() + df["redObjectives"].sum())
            * 100
        )

        blue_win_rate = metric_data["blueWins"].mean() * 100
        average_gold_diff = metric_data["blueGoldDiff"].mean()
        average_kill_diff = metric_data["kill_diff"].mean()
        objective_total = (
            metric_data["blueObjectives"].sum()
            + metric_data["redObjectives"].sum()
        )
        blue_objective_share = (
            metric_data["blueObjectives"].sum() / objective_total * 100
            if objective_total
            else 0.0
        )

        metric_1, metric_2, metric_3, metric_4 = st.columns(4, gap="small")
        metric_1.metric(
            "Vitórias do time azul",
            f"{blue_win_rate:.1f}%",
            delta=f"{blue_win_rate - baseline_blue_win_rate:+.1f} p.p. vs base",
            border=True,
            help="Proporção de partidas do recorte vencidas pelo time azul.",
        )
        metric_2.metric(
            "Vantagem média de ouro",
            f"{average_gold_diff:+,.0f}".replace(",", "."),
            delta=f"{average_gold_diff - baseline_gold_diff:+,.0f} vs base".replace(",", "."),
            border=True,
            help="blueGoldDiff: ouro azul menos ouro vermelho aos 10 minutos.",
        )
        metric_3.metric(
            "Vantagem média de abates",
            f"{average_kill_diff:+.2f}",
            delta=f"{average_kill_diff - baseline_kill_diff:+.2f} vs base",
            border=True,
            help="Abates do time azul menos abates do time vermelho.",
        )
        metric_4.metric(
            "Participação azul nos objetivos",
            f"{blue_objective_share:.1f}%",
            delta=f"{blue_objective_share - baseline_objective_share:+.1f} p.p. vs base",
            border=True,
            help="Parcela de dragões, arautos e torres do recorte conquistada pelo time azul.",
        )

        metric_data = metric_data.copy()
        metric_data["objective_control"] = np.select(
            [
                metric_data["objective_diff"] > 0,
                metric_data["objective_diff"] < 0,
            ],
            ["Vantagem Azul", "Vantagem Vermelha"],
            default="Empate",
        )
        objective_order = ["Vantagem Vermelha", "Empate", "Vantagem Azul"]
        objective_summary = (
            metric_data.groupby(
                ["objective_control", "team_label"],
                as_index=False,
                observed=True,
            )
            .agg(
                matches=("gameId", "count"),
                average_gold_diff=("blueGoldDiff", "mean"),
            )
        )
        objective_chart = (
            alt.Chart(objective_summary)
            .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
            .encode(
                x=alt.X(
                    "objective_control:N",
                    title="Controle de objetivos aos 10 minutos",
                    sort=objective_order,
                    axis=alt.Axis(labelAngle=0),
                ),
                xOffset="team_label:N",
                y=alt.Y("matches:Q", title="Partidas"),
                color=alt.Color(
                    "team_label:N",
                    title="Vencedor",
                    scale=WINNER_SCALE,
                ),
                tooltip=[
                    alt.Tooltip("objective_control:N", title="Controle"),
                    alt.Tooltip("team_label:N", title="Vencedor"),
                    alt.Tooltip("matches:Q", title="Partidas", format=","),
                    alt.Tooltip(
                        "average_gold_diff:Q",
                        title="Dif. média de ouro",
                        format="+,.0f",
                    ),
                ],
            )
            .properties(
                height=330,
                title="Vencedor final por controle de objetivos",
            )
        )
        with objectives_column:
            st.altair_chart(objective_chart, width="stretch")
