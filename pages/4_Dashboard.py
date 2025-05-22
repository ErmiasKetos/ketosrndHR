import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, JsCode
from utils.db import get_db, Candidate, get_current_job


def app():
    st.title("📊 Screening Dashboard")
    
    job = get_current_job()
    if not job:
        st.warning("Please set up a job in the Job Setup page before viewing the dashboard.")
        return

    # Fetch candidates for current job
    db = get_db()
    candidates = Candidate.select().where(Candidate.job_id == job.id)
    if not candidates:
        st.info("No candidates processed yet. Upload resumes to begin screening.")
        return

    # Prepare DataFrame
    df = candidates.to_dataframe()[['id', 'name', 'email', 'phone', 'score', 'summary', 'status']]
    df['summary'] = df['summary'].str.replace('\n', '<br>')  # HTML line breaks

    # AG Grid setup
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_column('summary', cellRenderer=JsCode("function(params) {return params.value;}"), autoHeight=True)
    gb.configure_selection(selection_mode='single', use_checkbox=True)
    gb.configure_column('id', headerName='', hide=True)
    grid_opts = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_opts,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode='MODEL_CHANGED',
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=False,
        allow_unsafe_jscode=True
    )

    selected = grid_response['selected_rows']
    if selected:
        sel = selected[0]
        st.markdown(f"### Advance **{sel['name']}** to next stage?")
        if st.button("Advance", key=sel['id']):
            Cand = Candidate.get(Candidate.id == sel['id'])
            Cand.status = 'Next Stage'
            Cand.save()
            st.success(f"{sel['name']} advanced to next stage.")
            st.experimental_rerun()

    # Export options
    with st.expander("Export Results"):
        st.download_button(
            label="Download CSV",
            data=df.to_csv(index=False),
            file_name=f"{job.title}_candidates.csv",
            mime='text/csv'
        )
        st.download_button(
            label="Download Excel",
            data=df.to_excel(index=False),
            file_name=f"{job.title}_candidates.xlsx",
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

