# Checklist Hoan Thanh Lab

## Muc tieu

Hoan thanh lab theo flow end-to-end: setup provider, xay chatbot baseline, xay ReAct agent, do log/metric, va nop bao cao.

## Pham vi

- In:
  - Setup moi truong va provider
  - Implement tool va agent loop
  - Chay test case, doc log, so sanh ket qua
  - Hoan thien bao cao nhom va ca nhan
- Out:
  - Toi uu production
  - Them tinh nang ngoai yeu cau lab

## Viec Can Lam

- [ ] Hoan thien `.env` va xac nhan provider/model dang goi duoc.
- [ ] Cai dependency bang `pip install -r requirements.txt`.
- [ ] Chay smoke test provider de kiem tra ket noi LLM.
- [ ] Tao it nhat 2 tools trong `src/tools/` voi mo ta ro rang.
- [ ] Lam chatbot baseline de thu cac bai toan nhieu buoc.
- [ ] Implement ReAct loop trong `src/agent/agent.py`:
  - Sinh `Thought`
  - Parse `Action`
  - Goi tool
  - Ghi `Observation`
  - Dung khi co `Final Answer`
- [ ] Them xu ly loi can ban: parse loi, tool khong ton tai, vuot `max_steps`.
- [ ] Chay nhieu test case de tao trace thanh cong va trace that bai.
- [ ] Doc log trong `logs/` va tong hop cac metric: token, latency, so step, parser error, hallucination, timeout.
- [ ] Cai tien agent v1 thanh v2 dua tren log va ket qua fail.
- [ ] So sanh chatbot vs agent bang bang ket qua/ngan gon nhan xet.
- [ ] Dien `report/group_report/TEMPLATE_GROUP_REPORT.md`.
- [ ] Dien `report/individual_reports/TEMPLATE_INDIVIDUAL_REPORT.md`.

## Xac nhan truoc khi nop

- [ ] Provider switch duoc it nhat giua 2 che do neu giang vien yeu cau.
- [ ] Co it nhat 1 failed trace va giai thich duoc vi sao fail.
- [ ] Co bang so sanh Chatbot vs ReAct Agent.
- [ ] Code chay duoc va report da dien day du.
