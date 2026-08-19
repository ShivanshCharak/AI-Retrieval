import { ChartBarMultiple } from "./component/Classification";
import { RetrievalEvaluationChart } from "./component/retrieval-evalation-chart";

export default function Dashboard(){
    return <>
    <h1>Evaluation</h1>
    <ChartBarMultiple/>
    <RetrievalEvaluationChart/>
    
    </>
}