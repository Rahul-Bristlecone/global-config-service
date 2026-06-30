from marshmallow import Schema, fields, validate


class GlobalConfigSchema(Schema):
    user_id = fields.Int(dump_only=True)
    # CONFIGKEY = fields.Int(dump_only=True)

    # -------------- General -----------------------
    DAYSBEFORENOTBEFORE = fields.Int(allow_none=True, load_default=0, dump_default=0)
    DAYSBEFORENOTAFTER = fields.Int(allow_none=True, load_default=0, dump_default=0)
    ALLOWHANDPICK = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))
    ALLOWOVERPICK = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))
    ALLOWPICKBYPRODWOSCAN = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))
    THIRDPARTYPACKER = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))
    INVGENMETHOD = fields.Str(allow_none=True)
    HIGHLIGHTDAYS = fields.Int(allow_none=True, load_default=0, dump_default=0)
    DAYSTOSHOW = fields.Int(allow_none=True, load_default=0, dump_default=0)
    DAYSTOSHOWDISCARDED = fields.Int(allow_none=True, load_default=0, dump_default=0)
    DAYSTOSHOWCANCELLED = fields.Int(allow_none=True, load_default=0, dump_default=0)
    ALLOWORDERFORWARDING = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))
    SHOWCOSTPRICE = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))

    # --------------- PDT/Label Printer ------------
    DISPLAYRACKLOCNONPDT = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))
    PDTCOMPORT = fields.Str(allow_none=True)
    PDTCOMSPEED = fields.Int(allow_none=True)
    PRINTASMICROSOFTPDF = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))
    PRINTERNAME = fields.Str(allow_none=True)
    PRINTERCOMPORT = fields.Str(allow_none=True)
    LABELPRINTERNAME = fields.Str(allow_none=True)
    MC3000PORTNO = fields.Str(allow_none=True)

    # --------------- Labels -----------------------
    SCMLABELFORMAT = fields.Str(allow_none=True)
    PRICELABELFORMAT = fields.Str(allow_none=True)
    CTNLABELFORMAT = fields.Str(allow_none=True)
    RATIOPACKLABELFORMAT = fields.Str(allow_none=True)
    TRADEUNITLABELFORMAT = fields.Str(allow_none=True)
    TRADEUNITLABELFORMAT2 = fields.Str(allow_none=True)
    BULKPALLETLABELFORMAT = fields.Str(allow_none=True)
    PRODUCEORDERLABELFORMAT = fields.Str(allow_none=True)
    ALLOWTUNPREFIX0AND9 = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))

    # ----------------- EDI ------------------------
    DEFAULTSENDMETHODKEY = fields.Str(allow_none=True)
    CHECKEVERYMINUTES = fields.Int(allow_none=True)

    # ---------------- Splits ----------------------
    ALLOWSPLITBYSTORE = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))
    MAXIMUMSPLITS = fields.Int(allow_none=True)

    # ----------------- New Orders -----------------
    NEWORDERACTION = fields.Int(allow_none=True, load_default=0, dump_default=0)
    DISPLAYNEWORDERFLAG = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))
    CLEARNEWORDFLGONCMD = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))
    CLEARNEWORDFLGONDISP = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))
    CLEARNEWORDFLGONPRNT = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))

    # ----------------- Completed Orders -----------
    COMPLETEQN1REQ = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))
    COMPLETEQN2REQ = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))
    COMPLETEQN3REQ = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))
    COMPLETEQN4REQ = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))
    COMPLETEQN5REQ = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))
    COMPLETEPWREQ = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))

    # ----------------- External -------------------
    ACCTCONFREQ = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))
    ALLOWACCTORDVALIDATION = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))
    EXTDLLNAME = fields.Str(allow_none=True)
    AUTOIMPORTEXTORD = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))

    # ------------------ ShutDown ------------------
    BACKUPAFTERSHUTDOWN = fields.Int(allow_none=True, load_default=0, dump_default=0, validate=validate.OneOf([0, 1]))
    BACKUPCOMMAND = fields.Str(allow_none=True)
    BACKUPPROGRAM = fields.Str(allow_none=True)
