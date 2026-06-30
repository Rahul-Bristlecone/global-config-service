from config.extentions import db


class GlobalConfigModel(db.Model):
	__tablename__ = "GLBCONFIG"

	user_id = db.Column(db.Integer, primary_key=True, index=True, nullable=False)
	# CONFIGKEY = db.Column(db.Integer, primary_key=True, nullable=False)
	
    # -------------- General -----------------------
	DAYSBEFORENOTBEFORE = db.Column(db.SmallInteger)
	DAYSBEFORENOTAFTER = db.Column(db.SmallInteger)
	ALLOWHANDPICK = db.Column(db.SmallInteger)
	ALLOWOVERPICK = db.Column(db.SmallInteger)
	ALLOWPICKBYPRODWOSCAN = db.Column(db.SmallInteger)
	THIRDPARTYPACKER = db.Column(db.SmallInteger)
	INVGENMETHOD = db.Column(db.String(30))
	HIGHLIGHTDAYS = db.Column(db.SmallInteger)
	DAYSTOSHOW = db.Column(db.SmallInteger)  # days to show completed order
	DAYSTOSHOWDISCARDED = db.Column(db.SmallInteger)
	DAYSTOSHOWCANCELLED = db.Column(db.SmallInteger)
	ALLOWORDERFORWARDING = db.Column(db.SmallInteger)
	SHOWCOSTPRICE = db.Column(db.SmallInteger)

	# --------------- PDT/Label Printer ------------
	DISPLAYRACKLOCNONPDT = db.Column(db.SmallInteger)
	PDTCOMPORT = db.Column(db.String(6))
	PDTCOMSPEED = db.Column(db.Integer)
	PRINTASMICROSOFTPDF = db.Column(db.SmallInteger)
	PRINTERNAME = db.Column(db.String(24))
	PRINTERCOMPORT = db.Column(db.String(6))
	LABELPRINTERNAME = db.Column(db.String(80))
	MC3000PORTNO = db.Column(db.String(24))
	
    # --------------- Labels -----------------------
	SCMLABELFORMAT = db.Column(db.String(20))
	PRICELABELFORMAT = db.Column(db.String(20))
	CTNLABELFORMAT = db.Column(db.String(20))
	RATIOPACKLABELFORMAT = db.Column(db.String(20))
	TRADEUNITLABELFORMAT = db.Column(db.String(20))
	TRADEUNITLABELFORMAT2 = db.Column(db.String(20))
	BULKPALLETLABELFORMAT = db.Column(db.String(20))
	PRODUCEORDERLABELFORMAT = db.Column(db.String(20))
	ALLOWTUNPREFIX0AND9 = db.Column(db.SmallInteger)
	
    # ----------------- EDI ------------------------
	DEFAULTSENDMETHODKEY = db.Column(db.String(12))
	CHECKEVERYMINUTES = db.Column(db.Integer)

	# ---------------- Splits ----------------------
	ALLOWSPLITBYSTORE = db.Column(db.SmallInteger)
	MAXIMUMSPLITS = db.Column(db.Integer)
	
    # ----------------- New Orders -----------------
	NEWORDERACTION = db.Column(db.SmallInteger)
	DISPLAYNEWORDERFLAG = db.Column(db.SmallInteger)
	CLEARNEWORDFLGONCMD = db.Column(db.SmallInteger)
	CLEARNEWORDFLGONDISP = db.Column(db.SmallInteger)
	CLEARNEWORDFLGONPRNT = db.Column(db.SmallInteger)
	
    # ----------------- Completed orders -----------
	COMPLETEQN1REQ = db.Column(db.SmallInteger)
	COMPLETEQN2REQ = db.Column(db.SmallInteger)
	COMPLETEQN3REQ = db.Column(db.SmallInteger)
	COMPLETEQN4REQ = db.Column(db.SmallInteger)
	COMPLETEQN5REQ = db.Column(db.SmallInteger)
	COMPLETEPWREQ = db.Column(db.SmallInteger)

	# ----------------- External -------------------
	ACCTCONFREQ = db.Column(db.SmallInteger)
	ALLOWACCTORDVALIDATION = db.Column(db.SmallInteger)
	EXTDLLNAME = db.Column(db.String(60))
	AUTOIMPORTEXTORD = db.Column(db.SmallInteger)
	
	# ------------------ ShutDown ------------------
	BACKUPAFTERSHUTDOWN = db.Column(db.SmallInteger)
	BACKUPCOMMAND = db.Column(db.String(60))
	BACKUPPROGRAM = db.Column(db.String(60))