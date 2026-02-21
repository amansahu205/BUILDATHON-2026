import { CaseLayout } from "@/components/layout/CaseLayout";
import { Outlet } from "react-router-dom";

const CaseDetailPage = () => {
  return (
    <CaseLayout>
      <Outlet />
    </CaseLayout>
  );
};

export default CaseDetailPage;
